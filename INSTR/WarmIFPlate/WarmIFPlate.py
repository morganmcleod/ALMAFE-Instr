class WarmIFPlate():
    def __init__(self, attenuator, inputSwitch, noiseSource, outputSwitch, yigFilter):
        self.attenuator = attenuator
        self.inputSwitch = inputSwitch
        self.noiseSource = noiseSource
        self.outputSwitch = outputSwitch
        self.yigFilter = yigFilter

    @property
    def device_info(self) -> dict:        
        reason = f"Attenuator:{'OK' if self.attenuator.connected() else 'ERROR'}\n"
        reason += f"Input switch:{'OK' if self.inputSwitch.connected() else 'ERROR'}\n"
        reason += f"Noise source:{'OK' if self.noiseSource.connected() else 'ERROR'}\n"
        reason += f"Output switch:{'OK' if self.noiseSource.connected() else 'ERROR'}\n"
        reason += f"YIG filter:{'OK' if self.yigFilter.connected() else 'ERROR'}"
        return {
            "name": "Warm IF Plate",
            "resource": self.resource,
            "connected": self.connected(),
            "reason": reason
        }             
        
    def connected(self) -> bool:
        return self.attenuator.connected() and \
            self.inputSwitch.connected() and \
            self.noiseSource.connected() and \
            self.outputSwitch.connected() and \
            self.yigFilter.connected()
