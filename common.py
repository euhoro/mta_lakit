from abc import ABC, abstractmethod
from typing import Dict

from pydantic import BaseModel, Field

COIN = "COIN"
BILL = "BILL"

B_200 = 200.0
B_100 = 100.0
B_20 = 20.0

C_10 = 10.0
C_1 = 1.0
C_5 = 5.0
C_01 = 0.1
C_001 = 0.01

BILLS_AND_COINS_FULL = {
    BILL: {B_200: 7, B_100: 4, B_20: 15},
    COIN: {C_10: 10, C_1: 10, C_5: 1, C_01: 12, C_001: 21},
}


class Inventory(BaseModel):
    BILL: Dict[float, int] = Field(default_factory=dict)
    COIN: Dict[float, int] = Field(default_factory=dict)


class InventoryService(ABC):
    @abstractmethod
    def read_inventory(self) -> Inventory:
        pass

    @abstractmethod
    def write_inventory(self, inventory: Inventory):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def acquire_lock(self):
        pass

    @abstractmethod
    def release_lock(self):
        pass
