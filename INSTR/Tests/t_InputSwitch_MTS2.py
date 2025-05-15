import time
from INSTR.InputSwitch.MTS2 import InputSelect, InputSwitch_MTS2

sw = InputSwitch_MTS2()
print(sw.device_info)

print("Selected: ", sw.selected)

sw.selected = InputSelect.POL0_LSB
time.sleep(1)
sw.selected = InputSelect.POL0_USB
time.sleep(1)
sw.selected = InputSelect.HOT_LOAD
time.sleep(1)
sw.selected = InputSelect.COLD_LOAD
time.sleep(1)
sw.selected = InputSelect.SPARE1
time.sleep(1)
sw.selected = InputSelect.SPARE2
time.sleep(1)
sw.selected = InputSelect.POL1_LSB
time.sleep(1)
sw.selected = InputSelect.POL1_USB
time.sleep(1)
sw.selected = InputSelect.HOT_LOAD
time.sleep(1)
sw.selected = InputSelect.COLD_LOAD
time.sleep(1)
sw.selected = InputSelect.SPARE1
time.sleep(1)
sw.selected = InputSelect.SPARE2
