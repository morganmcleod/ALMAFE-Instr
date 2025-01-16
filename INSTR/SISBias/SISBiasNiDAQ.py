import logging
import re
import time
import nidaqmx

class SISBias():
    """MTS SIS bias control via NI-DAQ
    """
    def __init__(self, simulate: bool = False):
        self.logger = logging.getLogger("ALMAFE-Instr")
        self.logger.info(f"MTS SIS Bias created")
        self.simulate = simulate
        if not simulate: 
            self.taskBias1Voltage = self._initTask("SET SIS1 V", isInput = False)
            self.taskBias2Voltage = self._initTask("SET SIS2 V", isInput = False)
            self.taskBias1Read = self._initTask("READ SIS1 IV", isInput = True)
            self.taskBias2Read = self._initTask("READ SIS2 IV", isInput = True)
            self.taskBias1Voltage.start()
            self.taskBias2Voltage.start()
            self.taskBias1Read.start()
            self.taskBias2Read.start()
        self.reset()

    def _initTask(self, lines: str, name: str = "", isInput: bool = True) -> nidaqmx.Task | None:
        def constructAssign(lines, name, isInput) -> nidaqmx.Task | None:
            try:
                task = nidaqmx.Task(name)
                if isInput:
                    task.ai_channels.add_ai_voltage_chan(lines, name)
                else:
                    task.ao_channels.add_ao_voltage_chan(lines, name)
                return task
            except:
                task = nidaqmx.Task(name)
                task.close()
                return None
        
        task = constructAssign(lines, name, isInput)
        if task is None:
            task = constructAssign(lines, name, isInput)
        return task
    
    def __del__(self):
        if not self.simulate:
            self.taskBias1Voltage.close()
            self.taskBias2Voltage.close()
            self.taskBias1Read.close()
            self.taskBias2Read.close()

    def reset(self):
        pass

    def read_bias(self, select: int):
        if select == 1:
            task = self.taskBias1Read
        elif select == 2:
            task = self.taskBias2Read

        task.read(100)