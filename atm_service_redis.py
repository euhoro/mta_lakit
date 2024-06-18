import threading
import time
import uuid
from abc import ABC, abstractmethod

import redis
import json
from pydantic import BaseModel, Field
from typing import Dict
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# from atm_repository_sqllite import SQLiteInventoryService
from atm_service_json_file import JSONFileInventoryService

#
# class Inventory(BaseModel):
#     BILL: Dict[float, int] = Field(default_factory=dict)
#     COIN: Dict[float, int] = Field(default_factory=dict)
#
#
# class InventoryService(ABC):
#     @abstractmethod
#     def read_inventory(self) -> Inventory:
#         pass
#
#     @abstractmethod
#     def write_inventory(self, inventory: Inventory):
#         pass
#
#     @abstractmethod
#     def restart(self):
#         pass
#
#     @abstractmethod
#     def acquire_lock(self):
#         pass
#
#     @abstractmethod
#     def release_lock(self):
#         pass
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


class ATMService:
    def __init__(self, inventory_service):
        self.inventory_service = inventory_service

    def perform_transaction(self, action, item_type, denomination, quantity, retries=3):
        while retries > 0:
            try:
                self.inventory_service.acquire_lock()
                try:
                    inventory = self.inventory_service.read_inventory()

                    denomination = float(denomination)
                    quantity = int(quantity)

                    if action == "put":
                        if item_type == "BILL":
                            if denomination in inventory.BILL:
                                inventory.BILL[denomination] += quantity
                            else:
                                inventory.BILL[denomination] = quantity
                        elif item_type == "COIN":
                            if denomination in inventory.COIN:
                                inventory.COIN[denomination] += quantity
                            else:
                                inventory.COIN[denomination] = quantity
                        self.inventory_service.write_inventory(inventory)
                        print(f"Put {quantity} of {denomination} {item_type.lower()}. New state: {inventory}")
                        return True

                    elif action == "retrieve":
                        if item_type == "BILL":
                            if denomination in inventory.BILL and inventory.BILL[denomination] >= quantity:
                                inventory.BILL[denomination] -= quantity
                            else:
                                return False
                        elif item_type == "COIN":
                            if denomination in inventory.COIN and inventory.COIN[denomination] >= quantity:
                                inventory.COIN[denomination] -= quantity
                            else:
                                return False
                        self.inventory_service.write_inventory(inventory)
                        print(f"Retrieved {quantity} of {denomination} {item_type.lower()}. New state: {inventory}")
                        return True

                    return False
                finally:
                    self.inventory_service.release_lock()
            except Exception as e:
                print(f"Error performing transaction: {e}. Retrying...")
                retries -= 1
                time.sleep(0.1)
        return False

    def get_total(self):
        self.inventory_service.acquire_lock()
        try:
            inventory = self.inventory_service.read_inventory()
            total = 0
            for denomination, quantity in inventory.BILL.items():
                total += float(denomination) * quantity
            for denomination, quantity in inventory.COIN.items():
                total += float(denomination) * quantity
            return total
        finally:
            self.inventory_service.release_lock()


# Stress Testing function
def stress_test(timeout=10):
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    inventory_service = RedisInventoryService(redis_client)

    # inventory_service = SQLiteInventoryService()
    # inventory_service = JSONFileInventoryService()
    atm_service = ATMService(inventory_service)

    # Restart to ensure a clean state
    inventory_service.restart()

    transaction_log = []
    num_threads = 20  # Set number of threads for stress testing
    actions = ["put", "retrieve"]
    item_types = ["BILL", "COIN"]
    denominations = {
        "BILL": [200.0, 100.0, 20.0],
        "COIN": [10.0, 5.0, 1.0, 0.1, 0.01]
    }

    def perform_random_transaction():
        action = random.choice(actions)
        item_type = random.choice(item_types)
        denomination = random.choice(denominations[item_type])
        quantity = random.randint(1, 10)

        success = atm_service.perform_transaction(action, item_type, denomination, quantity)
        if success:
            transaction_log.append((action, item_type, denomination, quantity))
            print(f"Transaction: {action.capitalize()} {quantity} of {denomination} {item_type.lower()}.")

    # Initial total
    initial_total = atm_service.get_total()
    print(f"Initial Total: {initial_total}")

    # Create threads for random transactions
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=perform_random_transaction)
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join(timeout)

    # Final total
    final_total = atm_service.get_total()
    print(f"Final Total: {final_total}")

    # Calculate the expected total from transaction log
    expected_total = initial_total
    for action, item_type, denomination, quantity in transaction_log:
        if action == "put":
            expected_total += float(denomination) * quantity
        elif action == "retrieve":
            expected_total -= float(denomination) * quantity

    print(f"Expected Total from Transactions: {expected_total}")

    # Assert the final total matches the expected total
    assert final_total == expected_total, "The final total does not match the expected total from transactions"


# Run the stress test with a timeout of 10 seconds
#stress_test(timeout=20)
