from INSTR.PowerSupply.AgilentE363xA import PowerSupply

class NoiseSource():
    """Noise diode implemented in terms of a Agilent E363xA power supply"""
    def __init__(self, resource = "GPIB0::5::INSTR", simulate = False):
        self.simulate = simulate
        if simulate:
            self.powerSupply = None
        else:
            self.powerSupply = PowerSupply(resource)
        self.reset()

    def reset(self) -> None:
        if not self.simulate:
            self.powerSupply.setOutputEnable(False)
            self.powerSupply.setCurrentLimit(0.04)
            self.powerSupply.setVoltage(28)

    def isConnected(self) -> bool:
        if simulate:
            return True
        else:
            return self.powerSupply.isConnected()

    def setEnable(self, enable: bool = False) -> None:
        if not simulate:
            self.powerSupply.setOutputEnable(enable)

