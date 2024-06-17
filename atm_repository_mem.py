from atm_repository import InventoryService


class InMemoryInventoryService(InventoryService):
    def __init__(self):
        self.inventory = {
            "BILL": {200: 7, 100: 4, 20: 15},
            "COIN": {10: 10, 1: 10, 5: 1, 0.1: 12, 0.01: 21}
        }

    def read_inventory(self):
        return self.inventory

    def write_inventory(self, inventory):
        self.inventory = inventory
