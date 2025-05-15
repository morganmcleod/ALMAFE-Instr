from typing import Tuple
import logging
from .ColdLoadBase import ColdLoadBase, FillMode, FillState

class AMI1720Simulator(ColdLoadBase):

    DEFAULT_TIMEOUT = 2500
    
    def __init__(self, idQuery=True, reset=True):
        """Constructor

        :param bool idQuery: If true, perform an ID query and check compatibility, defaults to True
        :param bool reset: If true, reset the instrument and set default configuration, defaults to True
        """
        self.logger = logging.getLogger("ALMAFE-Instr")
        self.logger.info(f"AMI1720 Simulator created")
        self.setFillMode(FillMode.NORMAL)
        self.fillState = FillState.CLOSED

    def idQuery(self) -> bool:
        """Perform an ID query and check compatibility

        :return bool: True if the instrument is compatible with this class.
        """
        self.model = "AMI1720Simulator"
        return True
    
    def reset(self) -> bool:
        """Reset the instrument and set default configuration

        :return bool: True if reset succeeded
        """
        return True
        
    def connected(self) -> bool:
        return True

    def setFillMode(self, fillMode: FillMode) -> None:
        """Set the fill mode in a device-dependent way

        :param FillMode defined above
        """
        self.fillMode = fillMode

    def getFillMode(self) -> FillMode:
        """Read the fillmode in a device-deptendent way

        :return FillMode defined above
        """
        return getattr(self, 'fillMode', FillMode.NORMAL)
    
    def getLevel(self) -> float:
        """Read LN2 level in percent, device-dependent

        :return float: Percent
        """
        return 99.0
    
    def setFillState(self, fillState: FillState) -> None:
        """Set the fill state in a device-dependent way

        :param FillState defined above
        """
        self.fillState = fillState

    def getFillState(self) -> FillState:
        """Read the fill state in a device-dependent way

        :return FillState defined above
        """
        return self.fillState

    def shouldPause(self, 
            minLevel: float = 20, 
            maxLevel: float = 150, 
            enablePause: bool = True) -> tuple[bool, str]:
        return False, ""