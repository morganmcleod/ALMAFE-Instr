import time
from INSTR.ColdLoad.TeragonLC10 import TeragonLC10

coldLoad = TeragonLC10()
coldLoad.idQuery()
print(coldLoad.model)

def display():
    print(f"fill mode: {coldLoad.getFillMode()}, fill state: {coldLoad.getFillState()}, valve: {coldLoad.currentValve}")

coldLoad.stopFill()
display()

time.sleep(5)
display()
coldLoad.startFill()

while True:
    time.sleep(5)
    display()

    shouldPause, msg = coldLoad.shouldPause()
    if shouldPause:
        print(f"pause measurement: '{msg}'")

