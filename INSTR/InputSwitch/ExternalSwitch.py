
from .Interface import InputSwitch_Interface, InputSelect
from INSTR.SwitchController.Agilent11713 import AttenuatorSwitchController

class ExternalSwitch(InputSwitch_Interface):

    POS1 = (True, False, False, False, False, False, False, False, False, False)
    POS2 = (False, True, False, False, False, False, False, False, False, False)
    POS3 = (False, False, True, False, False, False, False, False, False, False)

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
        self.position = None        
        if not self.simulate:
            self.switchController.setSwitches(self.switchController.RESET)
        self.select(InputSelect.POL0_USB)

    def is_connected(self) -> bool:
        if self.simulate:
            return True
        else:
            return self.switchController.isConnected()

    @property
    def selected(self) -> InputSelect:
        return self.position

    @selected.setter    
    def select(self, inputSelect: InputSelect):
        self.position = inputSelect
        if self.simulate:
            return
        if inputSelect in (InputSelect.POL0_USB, InputSelect.POL1_USB):
            self.switchController.setSwitches(self.POS1)
        elif inputSelect in (InputSelect.POL0_LSB, InputSelect.POL1_LSB):
            self.switchController.setSwitches(self.POS2)
        elif inputSelect == InputSelect.NOISE_SOURCE:
            self.switchController.setSwitches(self.POS3)

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
            self.select(InputSelect.POL0_USB)
        elif pol == 0 and sideband == 1:
            self.select(InputSelect.POL0_LSB)
        elif pol == 1 and sideband == 0:            
            self.select(InputSelect.POL1_USB)
        elif pol == 1 and sideband == 1:
            self.select(InputSelect.POL1_LSB)
        
    def select_noise_source(self) -> None:
        self.select(InputSelect.NOISE_SOURCE)
