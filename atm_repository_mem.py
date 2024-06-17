from atm_repository import InventoryService
from atm_repository_common import BILLS_AND_COINS


class InMemoryInventoryService(InventoryService):
    def __init__(self):
        self.inventory = BILLS_AND_COINS

    def read_inventory(self):
        return self.inventory

    def write_inventory(self, inventory):
        self.inventory = inventory
