import logging
import time
import nidaqmx
import nidaqmx.constants
from .Interface import InputSwitch_Interface, InputSelect

class DigitalOut0():
    
    def __init__(self, latchHoldTime: float = 0.3, simulate: bool = False):
        self.logger = logging.getLogger("ALMAFE-Instr")
        self.logger.info(f"DigitalOut0 created")
        self.latchHoldTime = latchHoldTime
        self.simulate = simulate
        if not simulate:        
            self.taskData = self._initTask('Dev1/port0/line0..2', 'data', False)
            self.taskAddress = self._initTask('Dev1/port0/line3..5', 'address', False)
            self.taskLatch = self._initTask('Dev1/port0/line6', 'address', False)

    def _initTask(self, lines: str, name: str = "", isInput: bool = True) -> nidaqmx.Task | None:
        def constructAssign(lines, name, isInput) -> nidaqmx.Task | None:
            try:
                task = nidaqmx.Task(name)
                if isInput:
                    task.di_channels.add_di_chan(lines, name)
                else:
                    task.do_channels.add_do_chan(lines, name)
                return task
            except:
                task = nidaqmx.Task(name)
                task.close()
                return None
        
        task = constructAssign(lines, name, isInput)
        if task is None:
            task = constructAssign(lines, name, isInput)
        return task

    def write(self, address: int, data: int):
        if not self.simulate:
            self.taskData.write(data, auto_start = True)
            self.taskAddress.write(address, auto_start = True)
            self.taskLatch.write(True)
            time.sleep(self.latchHoldTime)
            self.taskLatch.write(False)


class InputSwitch_MTS2(InputSwitch_Interface):
    ADDR_SET_USB = 0
    ADDR_SET_LSB = 1
    ADDR_SET_MIXER = 2    
    ADDR_RESET_MIXER = 3
    ADDR_SET_HOTLOAD = 4
    ADDR_RESET_HOTLOAD = 5
    ADDR_SET_COLDLOAD = 6
    ADDR_RESET_COLDLOAD = 7
    ADDR_SET_SPARE1 = 0
    ADDR_RESET_SPARE1 = 1
    ADDR_SET_SPARE2 = 2
    ADDR_RESET_SPARE2 = 3
    DATA_MUX_SELECT3 = 3
    DATA_MUX_SELECT4 = 4

    # Address (PA)	Mux select (DIO)	What
    # 0, 3  set USB
    # 1, 3  set LSB ("reset" on board)
    # 2, 3  set Mixer
    # 3, 3  reset Mixer
    # 4, 3  set Hot Load
    # 5, 3  reset Hot Load
    # 6, 3  set Cold Load
    # 7, 3  reset Cold Load
    # 0, 4  set Spare1
    # 1, 4  reset Spare1
    # 2, 4  set Spare2
    # 3, 4  reset Spare2

    # NOTE: won't work at room temp
    # unless ROOM TEMP switch resistor
    # is shorted.

    MODES = {
        InputSelect.POL0_USB: (ADDR_SET_USB, DATA_MUX_SELECT3, ADDR_RESET_MIXER),
        InputSelect.POL1_USB: (ADDR_SET_USB, DATA_MUX_SELECT3, ADDR_RESET_MIXER),
        InputSelect.POL0_LSB: (ADDR_SET_LSB, DATA_MUX_SELECT3, ADDR_RESET_MIXER),
        InputSelect.POL1_LSB: (ADDR_SET_LSB, DATA_MUX_SELECT3, ADDR_RESET_MIXER),
        InputSelect.COLD_LOAD: (ADDR_SET_COLDLOAD, DATA_MUX_SELECT3, ADDR_RESET_COLDLOAD),
        InputSelect.HOT_LOAD: (ADDR_SET_HOTLOAD, DATA_MUX_SELECT3, ADDR_RESET_HOTLOAD),
        InputSelect.SPARE1: (ADDR_SET_SPARE1, DATA_MUX_SELECT4, ADDR_RESET_SPARE1),
        InputSelect.SPARE2: (ADDR_SET_SPARE2, DATA_MUX_SELECT4, ADDR_RESET_SPARE2)
    }

    def __init__(self, simulate: bool = False):
        """Constructor
        """
        self.logger = logging.getLogger("ALMAFE-Instr")
        if simulate:
            self.logger.info(f"InputSwitch_MTS2 simulator created")
        else:
            self.logger.info(f"InputSwitch_MTS2 created")
        self.simulate = simulate
        self.digitalOut = DigitalOut0(simulate)
        self.reset()

    def reset(self) -> None:
        self.digitalOut.write(self.ADDR_RESET_MIXER, self.DATA_MUX_SELECT3)
        self.digitalOut.write(self.ADDR_RESET_HOTLOAD, self.DATA_MUX_SELECT3)
        self.digitalOut.write(self.ADDR_RESET_COLDLOAD, self.DATA_MUX_SELECT3)
        self.digitalOut.write(self.ADDR_RESET_SPARE1, self.DATA_MUX_SELECT4)
        self.digitalOut.write(self.ADDR_RESET_SPARE2, self.DATA_MUX_SELECT4)            
        self.selected = InputSelect.POL0_USB
        self.lastAddress = self.ADDR_RESET_MIXER
        self.lastMux = self.DATA_MUX_SELECT3

    @property
    def device_info(self) -> dict:
        return {
            "name": "B6v2 external input switch",
            "resource": "",
            "connected": self.connected()
        }
        
    def connected(self) -> bool:
        return True

    @property
    def selected(self) -> InputSelect:
        return self._selected

    @selected.setter    
    def selected(self, inputSelect: InputSelect):
        addr = self.MODES[inputSelect][0]
        mux = self.MODES[inputSelect][1]
        self.lastAddress = self.MODES[inputSelect][2]
        
        if inputSelect in (InputSelect.POL0_LSB, InputSelect.POL0_USB, InputSelect.POL1_LSB, InputSelect.POL1_USB):
            if self.lastAddress != self.ADDR_RESET_MIXER:
                # reset mixer
                self.digitalOut(self.ADDR_RESET_MIXER, self.DATA_MUX_SELECT3)
            # set mixer:
            self.digitalOut(self.ADDR_SET_MIXER, self.DATA_MUX_SELECT3)
            # set sideband:
            self.digitalOut(addr, mux)
            self.lastMux = mux
        else:
            # reset previous:
            self.digitalOut(self.lastAddress, self.lastMux)
            # set current:
            self.digitalOut(addr, mux)            
            self.lastMux = mux

    def select_pol_sideband(self, pol: int = 0, sideband: int | str = 'USB') -> None:
        if pol not in (0, 1):
            raise ValueError("InputSwitch_MTS2.select_pol_sideband: pol must be 0 or 1.")
        if isinstance(sideband, str):
            if sideband.upper() == 'USB':
                sideband = 0
            elif sideband.upper() == 'LSB':
                sideband = 1
            else:
                raise ValueError("InputSwitch_MTS2.select_pol_sideband: sideband must be 'USB', 0, 'LSB', or 1.")
        elif sideband not in (0, 1):
            raise ValueError("InputSwitch_MTS2.select_pol_sideband: sideband must be 'USB', 0, 'LSB', or 1.")
        
        if pol == 0 and sideband == 0:            
            self.selected = InputSelect.POL0_USB
        elif pol == 0 and sideband == 1:
            self.selected = InputSelect.POL0_LSB
        elif pol == 1 and sideband == 0:            
            self.selected = InputSelect.POL1_USB
        elif pol == 1 and sideband == 1:
            self.selected = InputSelect.POL1_LSB
        
    def select_noise_source(self) -> None:
        self.selected = InputSelect.NOISE_SOURCE
