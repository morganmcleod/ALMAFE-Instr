import logging
import time
from .BaseMXA import BaseMXA
from .schemas import *

class SpectrumAnalyzer(BaseMXA):

    def __init__(self, resource="TCPIP0::10.1.1.10::inst0::INSTR", idQuery=True, reset=True) -> None:
        """Constructor

        :param str resource: VISA resource string, defaults to "TCPIP0::10.1.1.10::inst0::INSTR"
        :param bool idQuery: If true, perform an ID query and check compatibility, defaults to True
        :param bool reset: If true, reset the instrument and set default configuration, defaults to True
        """
        self.logger = logging.getLogger("ALMAFE-Instr")
        self.logger.info(f"SpectrumAnalyzer created at {resource}")
        super().__init__(resource, idQuery, reset)
        self.settings = SpectrumAnalyzerSettings()
        self.isNarrowBand = False
        self.isWideBand = False
        self.configFreqStartStop(2e9, 22e9)

    def configureAll(self, settings: SpectrumAnalyzerSettings):
        self.settings = settings
        self.isNarrowBand = False
        self.configAcquisition(
            autoDetector = False,
            manualDetector = DetectorMode.AVERAGE,
            sweepPoints = settings.sweepPoints
        )
        self.configSweepCoupling(
            autoResolutionBW = settings.autoResolutionBW,
            resolutionBW = settings.resolutionBW,
            autoVideoBW = settings.autoVideoBW,
            videoBW = settings.videoBW,
            autoSweepTime = settings.autoSweepTime,
            sweepTime = settings.sweepTime
        )
        self.configTraceType(
            1, 
            TraceType.CLEAR_WRITE,
            enableUpdate = True,
            enableDisplay = True
        )
        self.configDetector(
            autoDetector = False,
            detector = DetectorMode.AVERAGE
        )
        self.configInternalPreamp(
            InternalPreamp.FULL_RANGE if settings.enableInternalPreamp else InternalPreamp.OFF
        )
        self.configLevel(
            autoAtten = False,
            manualAtten = settings.attenuation
        )
        self.configAveraging(
            count = settings.averagingCount if settings.enableAveraging else 1
        )

    def configNarrowBand(self, center: float, span: float) -> tuple[bool, str]:
        self.isNarrowBand = True
        self.configMarkerType(1, MarkerType.OFF)
        self.configAcquisition(autoDetector = False, manualDetector = DetectorMode.NORMAL, sweepPoints = 51)
        self.configFreqCenterSpan(center * 1e9, span * 1e9)
        self.configMarkerType(1, MarkerType.NORMAL)
        code, msg = self.errorQuery()
        return code == 0, msg

    def measureNarrowBand(self, averaging: int = 1, delay = 0) -> tuple[bool, str]:
        if not self.isNarrowBand:
            return False, "SpectrumAnalyzer.measureNarrowBand: wrong mode"
        self.configTraceType(1, TraceType.AVERAGE)
        self.configAveraging(averaging, AveragingType.RMS)
        if averaging > 1:
            self.restartTrace()
            time.sleep(delay)        
        iter = 3
        done = False
        # retry a couple times if we get an unreasonable power level:
        while iter > 0 and not done:
            iter -= 1
            self.readMarker()
            if -100 < self.markerY < 20:
                done = True
        if iter == 0:
            return False, "SpectrumAnalyzer.measureNarrowBand: too many retries"
        else:
            return True, ""
        
    def endNarrowBand(self) -> tuple[bool, str]:
        self.isNarrowBand = False
        self.configMarkerType(1, MarkerType.OFF)
    
    def configWideBand(self, center: float, span: float, sweepPoints: int = 161) -> tuple[bool, str]:
        self.isWideBand = True  
        self.configMarkerType(1, MarkerType.OFF)
        self.configAcquisition(autoDetector = False, manualDetector = DetectorMode.NORMAL, sweepPoints = sweepPoints)
        self.configFreqCenterSpan(center * 1e9, span * 1e9)
        self.configTraceType(1, TraceType.CLEAR_WRITE)
        self.configMarkerType(1, MarkerType.NORMAL)
        self.configMarkerCharacterisitcs(1, MarkerFunction.BAND_POWER, bandLeftHz = (center - span / 2) * 1e9, bandRightHz = (center + span / 2) * 1e9)
        code, msg = self.errorQuery()
        return code == 0, msg

    def measureWideBand(self, averaging: int = 1, delay = 0) -> tuple[bool, str]:
        if not self.isWideBand:
            return False, "SpectrumAnalyzer.measureWideBand: wrong mode"
        if averaging > 1:
            self.configTraceType(1, TraceType.AVERAGE)
            self.configAveraging(averaging, AveragingType.RMS)
            self.restartTrace()
            time.sleep(delay)
        iter = 3
        done = False
        # retry a couple times if we get an unreasonable power level:
        while iter > 0 and not done:
            iter -= 1
            self.readMarker()
            if -100 < self.markerY < 20:
                done = True
        if iter == 0:
            return True, "SpectrumAnalyzer.measureWideBand: too many retries"
        else:
            return True, "" 

    def endWideBand(self):
        self.isWideBand = False
        self.configMarkerType(1, MarkerType.OFF)

    def read(self, **kwargs) -> float | tuple[list[float], list[float]]:
        averaging = kwargs.get('averaging', 1)
        delay = kwargs.get('delay', 0)
        if self.isNarrowBand:
            success, msg = self.measureNarrowBand(averaging, delay)
            if success:
                return self.markerY
            else:
                self.logger.error(msg)
                return 0
        elif self.isWideBand:
            success, msg = self.measureWideBand(averaging, delay)
            if success:
                return self.markerY
            else:
                self.logger.error(msg)
                return 0
        else:
            success, msg = self.configAveraging(averaging)
            if not success:
                self.logger.error(msg)
            success, msg = self.restartTrace()
            if not success:
                self.logger.error(msg)
            time.sleep(delay)
            success, msg = self.readTrace()
            if success:
                return self.traceX, self.traceY
            else:
                self.logger.error(msg)
                return [], []
