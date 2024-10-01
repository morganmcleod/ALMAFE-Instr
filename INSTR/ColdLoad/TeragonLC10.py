import time
import nidaqmx
from .ColdLoadBase import ColdLoadBase, FillMode, FillState

class TeragonLC10(ColdLoadBase):

    FILL_TIMEOUT = 30
    POWER_OFF_WAIT = 2
    RESET_WAIT = 30
    

    def __init__(self):
        self.taskMainPower = self._initTask('Dev3/port0/line0', 'outMainPower', False)
        self.taskValveSwitch = self._initTask('Dev3/port0/line1', 'outValveSwitch', False)
        self.taskIsFilling = self._initTask('Dev3/port0/line2', 'inIsFilling', True, True)
        self.reset()

    def idQuery(self) -> bool:
        """Perform an ID query and check compatibility

        :return bool: True if the instrument is compatible with this class.
        """
        self.model = "TergaonLC10 LN2 controller"
        return True
    
    def reset(self) -> bool:
        """Reset the instrument and set default configuration

        :return bool: True if reset succeeded
        """
        self.setFillMode(FillMode.AUTO_CHANGE)
        self.setFillState(FillState.AUTO_OFF)
        self.fillTimeoutAt = None
        self.currentValve = None
        return True

    def _initTask(self, lines: str, name: str = "", isInput: bool = True, invert: bool = False) -> nidaqmx.Task | None:
        def constructAssign(lines, name, isInput, invert) -> nidaqmx.Task | None:
            task = nidaqmx.Task(name)
            try:                
                if isInput:
                    task.di_channels.add_di_chan(lines, name)
                    if invert:
                        task.di_channels[0].di_invert_lines = True
                else:
                    task.do_channels.add_do_chan(lines, name)
                    if invert:
                        task.do_channels[0].do_invert_lines = True
                return task
            except:
                task.close()
                return None
        
        task = constructAssign(lines, name, isInput, invert)
        if task is None:
            task = constructAssign(lines, name, isInput, invert)
        return task

    def __del__(self):
        self.taskMainPower.close()
        self.taskValveSwitch.close()
        self.taskIsFilling.close()
    
    def connected(self) -> bool:
        return True

    def setFillMode(self, fillMode: FillMode) -> None:
        """Set the fill mode in a device-dependent way

        :param FillMode defined above
        """
        self.fillMode = fillMode

    def getFillMode(self) -> FillMode:
        """Read the fillmode in a device-deptendent way

        :return FillMode defined above
        """
        return getattr(self, 'fillMode', FillMode.NORMAL)

    def getLevel(self) -> float:
        """Read LN2 level in percent, device-dependent

        :return float: Percent
        """
        return 99.0
    
    def setFillState(self, fillState: FillState) -> None:
        """Set the fill state in a device-dependent way

        :param FillState defined above
        """
        if fillState in (FillState.AUTO_ON, FillState.OPEN, FillState.FILLING):
            self.fillState = FillState.AUTO_ON
            self.taskMainPower.write(True)
            if self.currentValve is None:
                self.setCurrentValve(1)
            self.fillTimeoutAt = time.time() + self.FILL_TIMEOUT
        else:
            self.fillState = FillState
            self.taskMainPower.write(False)
    
    def getFillState(self) -> FillState:
        """Read the fill state in a device-dependent way

        :return FillState defined above
        """
        isFilling = self.taskIsFilling.read()
        if isFilling and self.fillState in (FillState.AUTO_ON, FillState.OPEN, FillState.FILLING):
            return FillState.FILLING
        else:
            return self.fillState

    def setCurrentValve(self, valve: int) -> None:
        if valve in (1, 2):
            self.currentValve = valve
            self.taskValveSwitch = bool(valve - 1)
            return True
        else:
            raise ValueError("TeragonLC10.setCurrentValve: valve must be 1 or 2")
        
    def shouldPause(self, enablePause: bool = True) -> tuple[bool, str]:
        """Should the calling measurement procedure pause and wait for cold load intervention?

        :param bool enablePause: If false generally return True = yes pause, except in error conditions.
        :return Tuple[bool, str]: Should pause?, and a description of why.
        """
        currentState = self.getFillState()
        if self.fillState == FillState.AUTO_ON and currentState == FillState.FILLING:
            if time.time() > self.fillTimeoutAt:
                if self.currentValve == 2:
                    return enablePause, f"Fill timed out at {self.fillTimeoutAt}, state is {currentState.name}, valve is {self.currentValve}"
                else:
                    self.setCurrentValve(2)
                    self.fillTimeoutAt = time.time() + self.FILL_TIMEOUT
                    return False, "Switched to valve 2."
        return False, ""
