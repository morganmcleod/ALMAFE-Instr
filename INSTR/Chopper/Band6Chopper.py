import time
import logging
import serial
from enum import Enum
from INSTR.Common.RemoveDelims import removeDelims
from INSTR.Common.Singleton import Singleton
from .Interface import Chopper_Interface, ChopperState

class Chopper(Singleton, Chopper_Interface):
    """The band 6 chopper is based on an Intelligent Motion Systems Panther LE2 stepper motor controller.
    There are reflective tape marks on the chopper wheel so that the half-clock (HC) and full-clock (FC)
    positions can be sensed, for homing and for reporting its current position.
    Monitor and control is via RS232. The CTS and DSR lines are used as digital inputs for the HC and FC signals.
    """

    def init(self, resource="COM1", openIsHot: bool = True, simulate: bool = False):
        """Constructor

        :param str resource: serial port to use, defaults to "COM1"
        :param bool findOpen: if True, index the chopper before returning. defaults to True
        :raises Exception: If the serial port cannot be opened.
        """
        self._openIsHot = openIsHot
        self.simulate = simulate
        self.logger = logging.getLogger("ALMAFE-CTS-Control")
        self.spinning = False        
        try:
            self.inst = serial.Serial(
                resource, 
                9600, 
                timeout=0.2, 
                write_timeout=0.1, 
                parity=serial.PARITY_NONE)
            if self.inst.is_open:
                self.inst.reset_input_buffer()
                self.inst.reset_output_buffer()
                self.reset()
            elif self.simulate:
                return
                
        except:
            if self.simulate:
                return

    def reset(self):
        """Reset the chopper to a known and indexed state, with default settings for open/close movement.
        """
        self.__hardStop()
        self.__variableResMode(True)
        self.__divideResolution(3)
        self.__setVelocity(initial = 50, slew = 500)
        self.__setCurrent(hold = 3, run = 15)
        self.__setRampSlope(accel = 3, decel = 3)
        self.__findOpen()
        self.spinning = False

    def isConnected(self) -> bool:
        if self.simulate:
            return True
        # request position
        read = self.__serialWrite("Z 0\r")
        return True if read else False

    def getState(self) -> ChopperState:
        """Get the chopper state

        :return State: one of OPEN, CLOSED, or TRANSITION
        """
        HC, FC = self.__getClockBits()
        if HC and FC: 
            return ChopperState.CLOSED
        elif HC and not FC: 
            return ChopperState.OPEN
        else: 
            return ChopperState.TRANSITION

    @property
    def openIsHot(self) -> bool:
        return self._openIsHot

    def isSpinning(self) -> bool:
        return self.spinning

    def spin(self, rps: float = 1.0):
        """Start spinning the chopper at a fixed revolutions per second (rps)

        :param float rps: how fast
        """
        self.__moveFixedVelocity(0)
        self.__setVelocity(initial= 20, slew = 400)
        self.__setCurrent(hold = 3, run = 15)
        self.__setRampSlope(accel = 1, decel = 1)
        # scale the requested rps to steps per second:
        self.__moveFixedVelocity(int(rps * 200 * 8))
        self.spinning = True

    def stop(self, hard:bool = False):
        """Stop the chopper

        :param bool hard: if true, issue a hard stop (no deceleration). defaults to False
        """
        if hard:
            self.__hardStop()
        else:
            self.__softStop()
        self.spinning = False

    def open(self):
        """Move the chopper to the open position
        """
        pos = self.__getPosition()
        # Any position that ends in 75 is open:
        new = 100 * (pos // 100) + 75
        self.__gotoPosition(new)
        if not self.__waitForStop():
            self.logger.debug("Chopper open: timeout")
        self.spinning = False
       
    def close(self):
        """Move the chopper to the closed position
        """
        pos = self.__getPosition()
        # Any position that ends in 25 is closed
        new = 100 * (pos // 100) + 25
        self.__gotoPosition(new)
        if not self.__waitForStop():
            self.logger.debug("Chopper close: timeout")
        self.spinning = False

    def gotoHot(self):
        if self._openIsHot:
            self.open()
        else:
            self.close()

    def gotoCold(self):
        if self._openIsHot:
            self.close()
        else:
            self.open()

    def gotoPosition(self, pos:int):
        """Go to the specified index position

        :param int pos: where to go
        """
        self.__gotoPosition(pos)
        self.__waitForStop()
        self.spinning = False

    def getPostion(self) -> int:
        """Get the current index position

        :return int: current position
        """
        return self.__getPosition()

    def __findOpen(self):
        """Index the chopper and move to the open position
        """
        self.__softStop()
        # start moving and wait for the full-clock bit to be 0:
        self.__moveFixedVelocity(speed = 300)
        timeout = False
        if not self.__waitForFC(False):
            timeout = True
        # continue until the FC is 1:
        if not self.__waitForFC(True):
            timeout = True
        # stop and back up slowly until FC is 0:
        self.__softStop()
        self.__moveFixedVelocity(-75)
        if not self.__waitForFC(False):
            timeout = True
        # stop and set the 0 index here:
        self.__hardStop()
        self.__setOrigin()
        time.sleep(0.200)
        # the open position is any that ends in 75:
        self.__gotoPosition(steps = 75)
        if not self.__waitForStop():
            timeout = True
        if timeout:
            self.logger.debug("Chopper __findOpen: timeout")

    def __waitForFC(self, stopValue:bool) -> bool:
        """Wait for the full-clock signal to have the specifed stopValue

        :param bool stopValue: do we want to stop on 1 or 0?
        :return bool: True if success, False if timeout
        """
        done = False
        iter = 300
        while not done and iter > 0:
            _, FC = self.__getClockBits()
            if FC == stopValue:
                done = True
            else:
                iter -= 1
                time.sleep(0.010)
        return iter > 0

    def __waitForStop(self) -> bool:
        """Wait for the chopper to stop motion

        :return bool: True if success, False if timeout
        """
        done = False
        iter = 300
        while not done and iter > 0:
            time.sleep(0.2)
            if not self.__isMoving():
                done = True
            else:
                iter -= 1
        return iter > 0

    def __hardStop(self):
        # the ESC character with no carriage return
        self.__serialWrite("\x1B")

    def __variableResMode(self, enable:bool):
        self.__serialWrite("H 1\r" if enable else "H 0\r")

    def __getClockBits(self) -> tuple[bool, bool]:
        """Get the half-clock (HC) and full-clock (FC) sensor bits.

        :return bool, bool: HC, FC
        """
        # On a 9-pin RS232 connector:
        # CTS corresponds to pin 8
        # DSR corresponds to pin 6
        # These clock signals are tied in to the RS232 cable connected to the chopper
        # motor controller.  These pins are unsed for chopper motor control so they were
        # available for use as trigger signal inputs.
        HC = self.inst.cts
        FC = self.inst.dsr
        return HC, FC

    def __setVelocity(self, initial:int, slew:int):
        self.__serialWrite(f"I {initial}\r")
        self.__serialWrite(f"V {slew}\r")

    def __divideResolution(self, step:int):
        # Sets the microstep resolution.
        # 3 = microsteps are 1/8 full step.
        self.__serialWrite(f"D {step}\r")

    def __setCurrent(self, hold:int, run:int):
        self.__serialWrite(f"Y {hold} {run}\r")

    def __setRampSlope(self, accel:int, decel:int):
        self.__serialWrite(f"K {accel} {decel}\r")
    
    def __moveFixedVelocity(self, speed:int):
        self.__serialWrite(f"M+{speed}\r")

    def __softStop(self):
        self.__serialWrite("@\r")
        time.sleep(0.1)

    def __setOrigin(self):
        self.__serialWrite("O\r")

    def __gotoPosition(self, steps:int):
        self.__serialWrite(f"R+{steps}\r")

    def __getPosition(self):
        read = self.__serialWrite("Z 0\r")
        read = removeDelims(read)
        if len(read) >= 3:
            currPos = int(float(read[2]))
            self.logger.debug(f"Chopper: currPos={currPos}")
            return currPos
        else:
            return 0

    def __isMoving(self):
        read = self.__serialWrite("^\r")
        read = removeDelims(read)
        if len(read) >= 2:
            status = int(read[1])
            __isMoving = status & 1
            # the status byte also has these values available:
            # isConstantVelocity = status & 2
            # isHoming = status & 8
            # isHunting = status & 16
            # isRamping = status & 32
            return __isMoving
        return False
       
    def __serialWrite(self, cmd:str) -> str | None:
        """Write to the serial device and read the reply

        :param str cmd: string to write
        :return str: string returned by the motor controller
        """
        try:
            cmd = bytes(cmd, 'utf8')
            num = self.inst.write(cmd)
            time.sleep(0.1)
            num = self.inst.in_waiting
            read = self.inst.read(num)
            self.logger.debug(read)
            return read.decode()
        except Exception as e:
            self.logger.exception(e)
            return None
