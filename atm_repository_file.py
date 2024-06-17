import fcntl
import json
import os

from atm_repository import InventoryService

INVENTORY_FILE = 'inventory.json'


class FileInventoryService(InventoryService):
    def __init__(self):
        if not os.path.exists(INVENTORY_FILE):
            initial_inventory = {
                "BILL": {200: 7, 100: 4, 20: 15},
                "COIN": {10: 10, 1: 10, 5: 1, 0.1: 12, 0.01: 21}
            }
            self.write_inventory(initial_inventory)

    def read_inventory(self):
        with open(INVENTORY_FILE, 'r') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            inventory = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)

        # Convert keys back to appropriate types
        inventory["BILL"] = {int(k): v for k, v in inventory["BILL"].items()}
        inventory["COIN"] = {float(k): v for k, v in inventory["COIN"].items()}

        return inventory

    def write_inventory(self, inventory):
        with open(INVENTORY_FILE, 'w') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            json.dump(inventory, file)
            fcntl.flock(file, fcntl.LOCK_UN)
