import fcntl
import json
import os
import time

from common import Inventory, InventoryService


class JSONFileInventoryService(InventoryService):
    def __init__(self, file_path='inventory.json'):
        self.file_path = file_path
        self.initial_inventory = Inventory(
            BILL={200.0: 7, 100.0: 4, 20.0: 15},
            COIN={10.0: 10, 1.0: 10, 5.0: 1, 0.1: 12, 0.01: 21}
        )
        self.restart()

    def _read_file(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.write_inventory(self.initial_inventory)
            return self.initial_inventory.dict()
        except json.JSONDecodeError:
            return self.initial_inventory.dict()

    def _write_file(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file)

    def read_inventory(self) -> Inventory:
        data = self._read_file()
        return Inventory(**data)

    def write_inventory(self, inventory: Inventory):
        data = inventory.dict()
        self._write_file(data)

    def restart(self):
        self.write_inventory(self.initial_inventory)

    def acquire_lock(self):
        pass
        # self.lock_file = open(self.file_path, 'a')
        # while True:
        #     try:
        #         fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        #         return True
        #     except BlockingIOError:
        #         time.sleep(0.001)  # Reduced sleep time to speed up retries

    def release_lock(self):
        pass
        # fcntl.flock(self.lock_file, fcntl.LOCK_UN)
        # self.lock_file.close()
