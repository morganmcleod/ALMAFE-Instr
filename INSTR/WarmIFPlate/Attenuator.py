from INSTR.SwitchController.Agilent11713 import AttenuatorSwitchController
import copy

class Attenuator():
    MAX_ATTENUATION = 121
    DIVISORS = (40, 40, 20, 10, 4, 4, 2, 1)
    RESET_SWITCHES = (True, True, True, True, True, True, True, True, False, False)

    def __init__(self, resource = "GPIB0::28::INSTR", reset = True, simulate = False):
        """Constructor

        :param str resource: VISA resource string, defaults to "GPIB0::9::INSTR"
        """
        # don't reset here because that would set attenuation to 0:
        self.simulate = simulate
        if simulate:
            self.switchController = None
        else:
            self.switchController = AttenuatorSwitchController(resource, reset = False)

        if reset:
            self.reset()

    def reset(self):
        # set attenuation to max:
        if not self.simulate:
            self.switchController.setSwitches(self.RESET_SWITCHES)
        self.value = self.MAX_ATTENUATION

    def connected(self) -> bool:
        if self.simulate:
            return True
        else:
            return self.switchController.connected()
    
    def setValue(self, atten: int = MAX_ATTENUATION):
        if atten < 0 or atten > self.MAX_ATTENUATION:
            atten = self.MAX_ATTENUATION
        
        self.value = atten

        remaining = copy.copy(atten)
        switches = []

        for div in self.DIVISORS:
            if remaining < div:
                switches.insert(0, False)
            else:
                remaining -= div
                switches.insert(0, True)

        switches.append(False)
        switches.append(False)
        if not self.simulate:     
            self.switchController.setSwitches(switches)

    def getValue(self):
        return self.value
