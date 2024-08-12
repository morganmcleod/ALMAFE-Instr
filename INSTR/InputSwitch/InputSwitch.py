from .Interface import InputSwitch_Interface, InputSelect
from INSTR.SwitchController.HP3488a import SwitchController, SwitchConfig, DigitalPort

class InputSwitch(InputSwitch_Interface):

    controlBits = {
        InputSelect.POL0_USB: 1,
        InputSelect.POL0_LSB: 2,
        InputSelect.POL1_USB: 4,
        InputSelect.POL1_LSB: 8,
        InputSelect.NOISE_SOURCE: 64,
        'Spare input 6': 32
    }

    def __init__(self, resource="GPIB0::9::INSTR", simulate: bool = False):
        """Constructor

        :param str resource: VISA resource string, defaults to "GPIB0::9::INSTR"
        """
        self.simulate = simulate
        self.resource = "simulated" if simulate else resource
        if simulate:
            self.switchController = None
        else:
            self.switchController = SwitchController(self.resource, writeConfig = SwitchConfig(
                slot = 1,
                port = DigitalPort.LOW_ORDER_8BIT
            ))
        self.reset()

    def reset(self) -> None:    
        self.position = None
        self.selected = InputSelect.POL0_USB

    @property
    def device_info(self) -> dict:
        return {
            "name": "Warm IF Plate input switch",
            "resource": self.resource,
            "connected": self.connected()
        }
        
    def connected(self) -> bool:
        if self.simulate:
            return True
        else:
            return self.switchController.connected()

    @property
    def selected(self) -> InputSelect:
        return self.position

    @selected.setter
    def selected(self, inputSelect: InputSelect):
        # send the compliment of the byte having the selected bit:
        self.position = inputSelect
        self.switchController.staticWrite(255 - self.controlBits[inputSelect])
    
    def select_pol_sideband(self, pol: int = 0, sideband: int | str = 'USB') -> None:
        if pol not in (0, 1):
            raise ValueError("InputSwitch.select_pol_sideband: pol must be 0 or 1.")
        if isinstance(sideband, str):
            if sideband.upper() == 'USB':
                sideband = 0
            elif sideband.upper() == 'LSB':
                sideband = 1
            else:
                raise ValueError("InputSwitch.select_pol_sideband: sideband must be 'USB', 0, 'LSB', or 1.")
        elif sideband not in (0, 1):
            raise ValueError("InputSwitch.select_pol_sideband: sideband must be 'USB', 0, 'LSB', or 1.")
        if pol == 0:
            if sideband == 0:
                self.selected = InputSelect.POL0_USB
            elif sideband == 1:
                self.selected = InputSelect.POL0_LSB
        else:
            if sideband == 0:
                self.selected = InputSelect.POL1_USB
            elif sideband == 1:
                self.selected = InputSelect.POL1_LSB

    def select_noise_source(self) -> None:
        self.selected = InputSelect.NOISE_SOURCE