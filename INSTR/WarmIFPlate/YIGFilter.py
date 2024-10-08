from INSTR.SwitchController.HP3488a import SwitchController, SwitchConfig, DigitalPort, DigitalMethod

class YIGFilter():
    """The YIG filter in the IF processor"""
    
    MIN_TUNING_MHZ = 1000       # lower limit in MHz
    MAX_TUNING_MHZ = 12400      # upper limit in MHz
    STEP_RESOLUTION = 2.7839    # resolution in MHz/step
    LATCH_BIT = 4096            # latch the new tuning

    def __init__(self, resource="GPIB0::9::INSTR", simulate = False):
        """Constructor

        :param str resource: VISA resource string, defaults to "GPIB0::13::INSTR"
        """
        self.simulate = simulate
        if simulate:
            self.SwitchController = None
        else:
            self.switchController = SwitchController(resource, writeConfig = SwitchConfig(
                slot = 3,
                port = DigitalPort.WORD_16BIT,
                method = DigitalMethod.ASCII
            ))
        self.minGHz = self.MIN_TUNING_MHZ / 1000
        self.maxGHz = self.MAX_TUNING_MHZ / 1000
        self.reset()

    def reset(self):
        self.setFrequency(self.minGHz)
        self.freqGhz = self.minGHz

    def connected(self) -> bool:
        if self.simulate:
            return True
        else:
            return self.switchController.connected()

    def setFrequency(self, freqGHz: float) -> None:
        if freqGHz < self.minGHz:
            freqGHz = self.minGHz
        elif freqGHz > self.maxGHz:
            freqGHz = self.maxGHz

        self.freqGhz = freqGHz
        # tuning word is the complement of the input value, scaled to 0..4095
        MHz = 1000 * freqGHz
        tuning = self.MAX_TUNING_MHZ - MHz
        tuning = tuning / self.STEP_RESOLUTION
        tuningWord = int(round(tuning))

        # we send the tuning word three times, the second time having the latch bit set:
        data = [tuningWord, tuningWord + self.LATCH_BIT, tuningWord]
        if not self.simulate:
            self.switchController.digitalWrite(data)

    def getFrequency(self) -> float:
        return self.freqGhz        

