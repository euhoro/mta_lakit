from abc import ABC, abstractmethod


class InventoryService(ABC):
    @abstractmethod
    def read_inventory(self):
        pass

    @abstractmethod
    def write_inventory(self, inventory):
        pass
