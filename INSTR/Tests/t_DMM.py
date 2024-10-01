import time
from INSTR.DMM.HP34401 import HP34401, Function, AutoZero, TriggerSource
from INSTR.TemperatureMonitor.Lakeshore218 import TemperatureMonitor

voltMeter = HP34401()
tempMonitor = TemperatureMonitor()

sample_count = 10
duration = 5

voltMeter.configureMeasurement(
    Function.DC_VOLTAGE, 
    autoRange = False, 
    manualRange = 0.1
)
voltMeter.configureAutoZero(AutoZero.OFF)
voltMeter.configureAveraging(Function.DC_VOLTAGE, 1)
voltMeter.inst.write(f"SAMP:COUN {sample_count};")
voltMeter.configureTrigger(TriggerSource.IMMEDIATE)

start = time.time()
endTime = start + duration
reads = []
temps = []
done = False
while not done:
    reads += voltMeter.read()
    temp, _ = tempMonitor.readSingle(7)
    temps.append(temp)
    # time.sleep(0.015)
    if time.time() > endTime:
        done = True
end = time.time()
rate = (end - start) / len(reads)
print(len(reads), rate)
print(reads)
print(len(temps))
print(temps)
