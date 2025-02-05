from INSTR.CurrentSource.Keithley24XX import CurrentSource, CurrentRange

c = CurrentSource()
c.setRearTerminals()
success, msg = c.setCurrentSource(0.025, 0.1, CurrentRange.BY_VALUE)
success, msg = c.setOutput(True)
print(c.readCurrent())
success, msg = c.setOutput(False)

