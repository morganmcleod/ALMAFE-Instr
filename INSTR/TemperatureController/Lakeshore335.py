import logging
import re
import time
from INSTR.Common.RemoveDelims import removeDelims
from INSTR.Common.VisaInstrument import VisaInstrument

class TemperatureController():
    """Lakeshore 335 cryogenic temperature controller
    """
    DEFAULT_TIMEOUT = 10000

    def __init__(self, resource="GPIB0::13::INSTR", idQuery=True, reset=True):
        """Constructor

        :param str resource: VISA resource string, defaults to "GPIB0::13::INSTR"
        :param bool idQuery: If true, perform an ID query and check compatibility, defaults to True
        :param bool reset: If true, reset the instrument and set default configuration, defaults to True
        """
        self.logger = logging.getLogger("ALMAFE-Instr")
        self.logger.info(f"Lakeshore335 created at {resource}")
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
        match = re.search(r"MODEL335", response, flags=re.IGNORECASE)
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
        time.sleep(0.5)
        # *ESE 52 - enables Command Error, Execution Error, and Query Error bits in the Standard Event Status register.
        # OPSTE 195 - enables Processor Communication Error, Calibration Error, Sensor Overload, and Sensor Alarming bits in the Operation Event register.
        # *SRE 160 - enables Operation Summary and Event Status Summary bits in the Status Byte.
        # *CLS - clears the bits in the Status Byte register, Standard Event Status register, and Operation Event register and terminates all pending operations.  Clears the interface, but not the controller.
        self.inst.write("*ESE 52;OPSTE 195;*SRE 160;*CLS")
        return True
    
    def read_temperature(self, input: str = "A", data_source: str = "K") -> float:
        """_summary_

        :param str input: can be "A" or "B".  Defaults to "A"
        :param str data_source: can be "K", "C", or "S" for Sensor Units.  Defaults to "K"
        :return float: temperature
        """
        result = self.inst.query(f"{data_source}RDG?{input}")
        result = removeDelims(result)
        return float(result[0])

    def start_pid_control(self, setpoint: float = 4.2) -> None:
        # OUTMODE <output>,<mode>,<input>,<powerup enable>
        # output1: mode 1 = closed loop PID, input A, powerup enable off
        self.inst.write("OUTMODE 1,1,1,0")
        # setpoint for PID control
        self.inst.write(f"SETP 1,{setpoint}")
        # output 2: off
        self.inst.write("RANGE 2,0")
        # output 1: low
        self.inst.write("RANGE 1,1")

    def start_mixer_heating(self, percent: float = 35) -> None:
        # output 1: off
        self.inst.write("RANGE 1,0")
        # output 2: mode 3 = open loop, input none, powerup enable off
        self.inst.write("OUTMODE 2,3,0,0")
        # output 2: manual output <percent>
        self.inst.write(f"MOUT 2,{percent}")
        # output 2: medium
        self.inst.write("RANGE 2,2")
    
    def setpoint(self, setpoint: float = 4.2) -> None:
        # setpoint for PID control
        self.inst.write(f"SETP 1,{setpoint}")
