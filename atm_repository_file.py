import fcntl
import json
import os

from atm_repository import InventoryService
from atm_repository_common import BILLS_AND_COINS

INVENTORY_FILE = 'inventory.json'


class FileInventoryService(InventoryService):
    def __init__(self):
        if not os.path.exists(INVENTORY_FILE):
            self.re_init()

    def re_init(self):
        initial_inventory = BILLS_AND_COINS
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

    def restart(self):
        self.re_init()
