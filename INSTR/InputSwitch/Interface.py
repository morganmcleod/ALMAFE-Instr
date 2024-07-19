from abc import ABC, abstractmethod
from enum import Enum

class InputSelect(Enum):
    POL0_USB = 0
    POL0_LSB = 1
    POL1_USB = 2
    POL1_LSB = 3    
    NOISE_SOURCE = 4

class InputSwitch_Interface(ABC):

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @property
    @abstractmethod
    def selected(self) -> InputSelect:
        pass
        
    @selected.setter
    @abstractmethod
    def selected(self, inputSelect: InputSelect):
        pass

    @abstractmethod
    def select_pol_sideband(self, pol: int = 0, sideband: int | str = 'USB') -> None:
        pass

    @abstractmethod
    def select_noise_source(self) -> None:
        pass

