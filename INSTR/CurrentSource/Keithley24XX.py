from enum import Enum
from INSTR.Common.RemoveDelims import removeDelims
from INSTR.Common.VisaInstrument import VisaInstrument
import re

class CurrentRange(Enum):
    DEFAULT_100UA = 'DEF'
    MINIMUM = 'MIN'
    MAXIMUM = 'MAX'
    BY_VALUE = 'byval'
    AUTO_ON = 'Auto On'
    AUTO_OFF = 'Auto Off'

class CurrentLevel(Enum):
    DEFAULT_0A = 'DEF'
    MINIMUM = 'MIN'
    MAXIMUM = 'MAX'
    BY_VALUE = 'byval'

class OutputImpedanceMode(Enum):
    HIGH = 'HIMP'
    NORMAL = 'NORM'
    ZERO = 'ZERO'
    GUARD = 'GUARD'

class CurrentSource():

    DEFAULT_TIMEOUT = 15000     # milliseconds

    def __init__(self, resource="GPIB0::25::INSTR", idQuery=True, reset=True):
        self.mfr = None
        self.model = None
        self.inst = VisaInstrument(resource, timeout = self.DEFAULT_TIMEOUT)
        if reset:
            self.reset()
        ok = self.isConnected()
        if ok and idQuery:
            ok = self.idQuery()
        if ok and reset:
            ok = self.reset()

    def __del__(self):
        """Destructor
        """
        self.inst.close()

    def isConnected(self) -> bool:
        if not self.inst.connected:
            return False
        try:
            result = self.inst.query("*ESR?")
            result = removeDelims(result)
            return len(result) > 0
        except:
            return False
        
    def idQuery(self) -> bool:
        """Perform an ID query and check compatibility

        :return bool: True if the instrument is compatible with this class.
        """
        self.mfr = "KEITHLEY"
        self.model = self.inst.query("*IDN?")
        return True
    
        match = re.match(r"[ ]*((AGILENT|KEYSIGHT)\s+TECHNOLOGIES|HEWLETT-PACKARD)\s*\,", response, flags=re.IGNORECASE)
        if match:
            self.mfr = match.group()
            match = re.search("(E3631|E3632|E3633|E3634)", response)
            if match:
                self.model = match.group()
            else:
                self.model = response.split(',')[1:4]
            self.logger.debug(self.mfr + " " + self.model)
            return True
        return False
    
    def reset(self):
        """Reset the instrument and set default configuration

        :return bool: True if instrument responed to Operation Complete query
        """
        if self.inst.query("*RST;*OPC?"):
            return True
        else:
            return False
        
    def setCurrentSource(self, 
            currentA: float,
            rangeA: float = 0,
            rangeSelect: CurrentRange = CurrentRange.MAXIMUM,
            levelSelect: CurrentLevel = CurrentLevel.BY_VALUE
            ) -> tuple[bool, str]:
        success = True
        msg = ""
        # only fixed mode supported in this version:
        self.inst.write(":SOUR1:CURR:MODE FIX;")

        if rangeSelect == CurrentRange.BY_VALUE:
            self.inst.write(f":SOUR1:CURR:RANG {rangeA:.4e}")
        else:
            self.inst.write(f":SOUR1:CURR:RANG {rangeSelect.value}")

        if levelSelect == CurrentLevel.BY_VALUE:
            if currentA < -0.26:
                currentA = -0.26
                msg = "CurrentSource.setCurrent: limited current to -0.26 A"
            elif currentA > 0.26:
                currentA = 0.26
                msg = "CurrentSource.setCurrent: limited current to +0.26 A"
            self.inst.write(f":SOUR1:CURR {currentA:.4e};")
        else:        
            self.inst.write(f":SOUR1:CURR {levelSelect.value};")
        return success, msg
    
    def setOutput(self, 
            enable: bool, 
            interlockState: bool = False, 
            impedanceMode: OutputImpedanceMode = OutputImpedanceMode.NORMAL
            ) -> tuple[bool, str]:
        success = True
        msg = ""
        self.inst.write(f":OUTP:SMODE {impedanceMode.value};")
        self.inst.write(f"Interlock:State {'On' if interlockState else 'Off'};")
        self.inst.write(f":OUTP {'On' if enable else 'Off'};")
        return success, msg
    