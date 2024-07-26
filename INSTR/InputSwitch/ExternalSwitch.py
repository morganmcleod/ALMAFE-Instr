
from .Interface import InputSwitch_Interface, InputSelect
from INSTR.SwitchController.Agilent11713 import AttenuatorSwitchController

class ExternalSwitch(InputSwitch_Interface):

    def __init__(self, resource="GPIB0::29::INSTR", simulate: bool = False):
        """Constructor

        :param str resource: VISA resource string,
        """
        self.simulate = simulate
        if simulate:
            self.switchController = None
        else:
            self.switchController = AttenuatorSwitchController(resource)
        self.reset()

    def reset(self) -> None:
        if not self.simulate:
            self.switchController.setSwitches(self.switchController.RESET)
        self.selected = InputSelect.POL0_USB

    def is_connected(self) -> bool:
        if self.simulate:
            return True
        else:
            return self.switchController.isConnected()

    @property
    def selected(self) -> InputSelect:
        return self._selected

    @selected.setter    
    def selected(self, inputSelect: InputSelect):
        self._selected = inputSelect
        if self.simulate:
            return
        switches = [False] * 10
        switches[inputSelect.value] = True
        self.switchController.setSwitches(switches)

    def select_pol_sideband(self, pol: int = 0, sideband: int | str = 'USB') -> None:
        if pol not in (0, 1):
            raise ValueError("ExternalSwitch.select_pol_sideband: pol must be 0 or 1.")
        if isinstance(sideband, str):
            if sideband.upper() == 'USB':
                sideband = 0
            elif sideband.upper() == 'LSB':
                sideband = 1
            else:
                raise ValueError("ExternalSwitch.select_pol_sideband: sideband must be 'USB', 0, 'LSB', or 1.")
        elif sideband not in (0, 1):
            raise ValueError("ExternalSwitch.select_pol_sideband: sideband must be 'USB', 0, 'LSB', or 1.")
        
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
