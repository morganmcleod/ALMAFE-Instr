from abc import ABC, abstractmethod
from enum import Enum

class ChopperState(Enum):
    OPEN = 0
    TRANSITION = 1
    CLOSED = 2
    SPINNING = 3

class Chopper_Interface(ABC):
   
    @abstractmethod
    def reset(self):
        """Reset the chopper to a known and indexed state, with default settings for open/close movement.
        """
        pass

    @abstractmethod
    def isConnected(self) -> bool:
        pass

    @abstractmethod
    def getState(self) -> ChopperState:
        """Get the chopper state

        :return ChopperState: one of OPEN, CLOSED, TRANSITION
        """
        pass

    @property
    @abstractmethod
    def openIsHot(self) -> bool:
        pass
    
    @abstractmethod
    def isSpinning(self) -> bool:
        pass

    @abstractmethod
    def spin(self, rps:float = 1.0):
        """Start spinning the chopper at a fixed revolutions per second (rps)

        :param float rps: how fast
        """
        pass

    @abstractmethod
    def stop(self, hard:bool = False):
        """Stop the chopper

        :param bool hard: if true, issue a hard stop (no deceleration). defaults to False
        """
        pass

    @abstractmethod
    def open(self):
        """Move the chopper to the open position
        """
        pass
       
    @abstractmethod
    def close(self):
        """Move the chopper to the closed position
        """
        pass

    @abstractmethod
    def gotoHot(self):
        pass

    @abstractmethod
    def gotoCold(self):
        pass
