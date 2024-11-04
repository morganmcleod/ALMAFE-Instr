from INSTR.PowerMeter.KeysightE441X import PowerMeter

pm = PowerMeter()

for i in range(10):
    pw = pm.read()
    print(pw)
