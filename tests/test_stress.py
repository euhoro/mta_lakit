
# Stress Testing function
import threading
from random import random

import redis

from atm_service import ATMService
from atm_service_redis import RedisInventoryService
from common import COIN, BILL

import pytest
@pytest.mark.long
def stress_check(timeout=10):
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
    item_types = [BILL, COIN]
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


def test_stress():
    stress_check()