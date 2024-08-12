import time
import nidaqmx
from INSTR.Common.Singleton import Singleton
from .Interface import Chopper_Interface, ChopperState

class Chopper(Chopper_Interface, Singleton):

    def init(self, openIsHot: bool = False, simulate: bool = False):
        self._openIsHot = openIsHot
        self.simulate = simulate
        if not simulate:        
            self.taskBusy = self._initTask('Dev2/port0/line6', 'inBusy', True)
            self.taskSensor = self._initTask('Dev2/port0/line2', 'inSensor', True)
            self.taskSpeed = self._initTask('Dev2/port0/line1', 'outSpeed', False)
            self.taskOpenClose = self._initTask('Dev2/port0/line3', 'outOpenClose', False)
            self.taskSpin = self._initTask('Dev2/port0/line4', 'outSpin', False)
            self.taskEnable = self._initTask('Dev2/port0/line5', 'outEnable', False)
            self.taskSensor.start()
            self.taskBusy.start()
            self.taskSpeed.start()
            self.taskOpenClose.start()
            self.taskSpin.start()
            self.taskEnable.start()
        self.reset()

    def _initTask(self, lines: str, name: str = "", isInput: bool = True) -> nidaqmx.Task | None:
        def constructAssign(lines, name, isInput) -> nidaqmx.Task | None:
            try:
                task = nidaqmx.Task(name)
                if isInput:
                    task.di_channels.add_di_chan(lines, name)
                    task.di_channels[0].di_invert_lines = True
                else:
                    task.do_channels.add_do_chan(lines, name)
                    task.do_channels[0].do_invert_lines = True
                return task
            except:
                task = nidaqmx.Task(name)
                task.close()
                return None
        
        task = constructAssign(lines, name, isInput)
        if task is None:
            task = constructAssign(lines, name, isInput)
        return task

    def __del__(self):
        self.setMotorEnable(False)
        if not self.simulate:
            self.taskSensor.close()
            self.taskBusy.close()
            self.taskSpeed.close()
            self.taskOpenClose.close()
            self.taskSpin.close()
            self.taskEnable.close()

    def reset(self):
        """Reset the chopper to a known and indexed state, with default settings for open/close movement.
        """
        # disable the motor        
        self.setMotorEnable(False)
        # set spinning to stopped
        self.taskSpin.write(False)
        self.spinning = False
        # set position to closed
        self.close()
        # set speed to slow
        self.setSpeedSlow(True)
        time.sleep(0.1)
        # enable the motor
        self.setMotorEnable(True)
        # wait for move:
        self._waitBusy()
        
    def _waitBusy(self, timeout = 10):
        if self.simulate:
            time.sleep(1)
            return

        endTime = time.time() + timeout
        busy = True
        while busy and time.time() <= endTime:
            busy = self.taskBusy.read()
            time.sleep(0.010)

    def connected(self) -> bool:
        if self.simulate:
            return True
        else:
            return not self.taskEnable.is_task_done()
    
    def getState(self) -> ChopperState:
        """Get the chopper state

        :return ChopperState: one of OPEN, CLOSED, TRANSITION
        """
        if self.simulate:
            return ChopperState.TRANSITION

        state = self.taskSensor.read()
        if not self.spinning:
            return ChopperState.CLOSED if state else ChopperState.OPEN
    
    @property
    def openIsHot(self) -> bool:
        return self._openIsHot
        
    def isSpinning(self) -> bool:
        return self.isSpinning

    def spin(self, rps: float = 1.0):
        """Start spinning the chopper at a fixed revolutions per second (rps)

        :param float rps: how fast
        """
        if not self.simulate:
            self.taskSpin.write(True)
        self.spinning = True
        self.lastTransition = None
    
    def stop(self, hard:bool = False):
        """Stop the chopper

        :param bool hard: if true, issue a hard stop (no deceleration). defaults to False
        """
        if not self.simulate:
            self.taskSpin.write(False)
        self.spinning = False
        self.lastTransition = None
        self.reset()
    
    def open(self):
        """Move the chopper to the open position
        """
        if self.simulate:
            return

        self.taskOpenClose.write(False)
        if not self.spinning:
            self.taskOpenClose.write(False)
            self.lastState = ChopperState.OPEN
            self.lastTransition = None
            self._waitBusy()
    
    def close(self):
        """Move the chopper to the closed position
        """
        if self.simulate:
            return
        
        if not self.spinning:
            self.taskOpenClose.write(True)
            self.lastState = ChopperState.CLOSED
            self.lastTransition = None
            self._waitBusy()
    
    def gotoHot(self):
        if self._openIsHot:
            self.open()
        else:
            self.close()

    def gotoCold(self):
        if self._openIsHot:
            self.close()
        else:
            self.open()

    def setMotorEnable(self, value: bool):
        if not self.simulate:
            self.taskEnable.write(value)
        self.motorEnable = value

    def setSpeedSlow(self, value: bool):
        if not self.simulate:
            self.taskSpeed.write(value)
        self.speedFast = value
        