import logging
from .schemas import Channel, Trigger, StdErrConfig, StdErrResult
from ALMAFE.basic.Units import Units
from time import time
from statistics import mean, stdev
from math import sqrt

class PowerMeterSimulator():

    def __init__(self):
        self.logger = logging.getLogger("ALMAFE-Instr")
        self.logger.info(f"PowerMeterSimulator created")
        self.settings = {Channel.A : {}, Channel.B: {}}
        self.setDefaults()
        
    def reset(self):
        pass
    
    def connected(self) -> bool:
        return True
    
    def setDefaults(self):
        """Set instrument defaults so that the front panel shows live readings

        :return bool: True if instrument responed to Operation Complete query
        """
        ok = self.setUnits(Units.DBM)
        if ok:
            ok = self.setFastMode(False)
        if ok:
            ok = self.disableAveraging()
        return ok

    def setTimeout(self, timeoutMs: int = None):
        """Set the VISA timeout

        :param int timeoutMs: milliseconds
        """
        pass

    def setUnits(self, units: Units, channel = None):
        if channel is None:
            channel = Channel.A
        self.settings[channel]['units'] = units
        return True

    def setFastMode(self, fastMode:bool, channel = None):
        """Set/clear 200 readings/second fast mode

        :param fastMode: set fast mode if true
        :param Channel channel: which channel to configure, defaults to None which configures both channels if supported
        :return bool: True if instrument responed to Operation Complete query
        """
        if channel is None:
            channel = Channel.A
        self.settings[channel]['fastMode'] = fastMode
        return True
    
    def disableAveraging(self, channel = None):
        """Set the display to show both channels, if applicable, turns off averaging and sets the CW frequency to 6 GHz

        :param Channel channel: which channel to configure, defaults to None which configures both channels if supported
        :return bool: True if instrument responed to Operation Complete query
        """        
        return True

    def autoRead(self, channel = Channel.A):
        """Perform an auto-read which takes as long as needed to get (typically) three digits of resolution
        
        :param Channel channel: which channel to read, defaults to Channel.A
        :return float: power level
        """
        return -1.0
        
    def averagingRead(self, config: StdErrConfig, channel = Channel.A):
        """Read multiple samples and average, as configured by StdErrConfig

        :param config: StdErrConfig to set up the measurement requirements.  See StdErrConfig for details.
        :param Channel channel: which channel to read, defaults to Channel.A
        :return StdErrResult: see StdErrResult for details.
        """
        return StdErrResult(
            success = True,
            N = 10,
            mean = -1.0,
            stdErr = 0.001,
            CI95U = -1.001,
            CI95L = -0.999,
            useCase = StdErrConfig.UseCase.MIN_SAMPLES,
            time = 0.001
        )

    def read(self, channel = Channel.A, averaging = 1):
        """Read the instrument once, taking into account the configured Measurement

        :param Channel channel: which channel to measure, defaults to Channel.A
        :return float: measured power level
        """
        return -1.0
