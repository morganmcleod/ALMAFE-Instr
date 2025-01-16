import logging
import re
import time
from INSTR.Common.RemoveDelims import removeDelims
from INSTR.Common.VisaInstrument import VisaInstrument

class MagnetCurrent():
    """ Magnet current control implemented in terms of a Keithley 2400 current source
    """
    DEFAULT_TIMEOUT = 10000

    def __init__(self, resource="GPIB0::6::INSTR", idQuery=True, reset=True):
        """Constructor

        :param str resource: VISA resource string, defaults to "GPIB0::6::INSTR"
        :param bool idQuery: If true, perform an ID query and check compatibility, defaults to True
        :param bool reset: If true, reset the instrument and set default configuration, defaults to True
        """
        self.logger = logging.getLogger("ALMAFE-Instr")
        self.logger.info(f"MagnetCurrent(Keithley 2400) created at {resource}")
        self.inst = VisaInstrument(resource, timeout = self.DEFAULT_TIMEOUT, read_termination = '\n', write_termination = '\n')
        ok = self.connected()
        if ok and idQuery:
            ok = self.idQuery()
        if ok and reset:
            ok = self.reset()

    def __del__(self):
        """Destructor
        """
        if self.inst:
            self.inst.close()
            self.inst = None

    def connected(self) -> bool:
        if not self.inst.connected:
            return False
        try:
            result = self.inst.query("*ESR?\r")
            result = removeDelims(result)
            return len(result) > 0
        except:
            return False
        
    def idQuery(self) -> bool:
        """Perform an ID query and check compatibility

        :return bool: True if the instrument is compatible with this class.
        """
        if not self.inst:
            return False

        mfr = None
        model = None
        response = self.inst.query("*IDN?\r")
        match = re.search(r"2400", response, flags=re.IGNORECASE)
        if match:
            mfr = "Lakeshore"
            model = match.group()

        if mfr and model:
            self.logger.debug(mfr + " " + model)
            return True
        return False
    
    def reset(self) -> bool:
        """Reset the instrument and set default configuration

        :return bool: True if instrument responed to Operation Complete query
        """
        self.inst.write("*RST")
        # configure current source to use rear terminals:
        self.inst.write("ROUT:TERM:REAR")        
        self.output_control(True)
        # powerline cycles = 1, current compliance 0.000105
        self.inst.write(":SENS:CURR:NPLC 1.0E+0;PROT 1.05E-4;")
        # range 0.1 amps
        self.inst.write(":CURR:RANG 1.0E-1;")
        return True
    
    def output_control(self, enable: bool, interlock_state: bool = False, impedance_mode: str = "NORM"):
        """ Enable/disable output

        :param bool enable
        :param interlock_state: bool disable or enable, defaults to False
        :param str impedance_mode: can be "NORM", "HIMP", "ZERO" or "GUARD".  Defaults to "NORM".

        """
        self.inst.write(f":OUTP:SMODE {impedance_mode};INTERLOCK:STATE {'ON' if interlock_state else 'OFF'};")
        self.inst.write(f":OUTP {'ON' if enable else 'OFF'}")
        
    def set_current(self, current_mA: float) -> bool:
        if -0.5 < current_mA < 0.5:
            self.inst.write(":SOUR1:FUNC:CURR;SOUR1:CURR:MODE FIX;SOUR1:CURR:RANG 1.0E-1;")
            self.inst.wriee(f":SOUR1:CURR {current_mA:.3e};")
            self.output_control(True)
            return True
        else:
            return False
    
    def read_current(self) -> float:
        result = self.inst.query(":MEAS:CURR:DC?")
        result = removeDelims(result)
        return float(result[0])
    