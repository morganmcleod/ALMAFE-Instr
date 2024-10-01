import time
from INSTR.DMM.HP34401 import HP34401, Function, AutoZero, TriggerSource

voltMeter = HP34401()
voltMeter.configureMeasurement(
    Function.DC_VOLTAGE, 
    autoRange = False, 
    manualRange = 0.1
)
voltMeter.configureAutoZero(AutoZero.OFF)
voltMeter.configureAveraging(Function.DC_VOLTAGE, 1)
voltMeter.configureTrigger(TriggerSource.IMMEDIATE)
voltMeter.inst.write("SAMP:COUN 10;")
voltMeter.inst.write("INIT;")

count = 1
start = time.time()
reads = []
for i in range(count):
    reads += voltMeter.readSinglePoint()
    time.sleep(0.01)
end = time.time()
rate = (end - start) / len(reads)
print(len(reads), rate)
print(reads)
