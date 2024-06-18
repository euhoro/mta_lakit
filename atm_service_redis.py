import time
import uuid

from common import InventoryService, Inventory


class RedisInventoryService(InventoryService):
    def __init__(self, client, lock_name='inventory_lock', lock_timeout=10):
        self.client = client
        self.lock_name = lock_name
        self.lock_timeout = lock_timeout
        self.lock_value = str(uuid.uuid4())
        self.initial_inventory = Inventory(
            BILL={200.0: 7, 100.0: 4, 20.0: 15},
            COIN={10.0: 10, 1.0: 10, 5.0: 1, 0.1: 12, 0.01: 21}
        )

    def read_inventory(self) -> Inventory:
        inventory_json = self.client.get('atm_inventory')
        if inventory_json is None:
            return self.initial_inventory
        return Inventory.parse_raw(inventory_json)

    def write_inventory(self, inventory: Inventory):
        self.client.set('atm_inventory', inventory.json())

    def restart(self):
        self.write_inventory(self.initial_inventory)

    def acquire_lock(self):
        while True:
            if self.client.setnx(self.lock_name, self.lock_value):
                self.client.expire(self.lock_name, self.lock_timeout)
                return True
            elif self.client.ttl(self.lock_name) == -1:
                self.client.expire(self.lock_name, self.lock_timeout)
            time.sleep(0.001)  # Reduced sleep time to speed up retries

    def release_lock(self):
        if self.client.get(self.lock_name) == self.lock_value:
            self.client.delete(self.lock_name)