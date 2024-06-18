import os
import time

from atm_service_redis import RedisInventoryService
from common import Inventory

MAX_AMOUNT = 2000

ZERO_MIN_AMOUNT = 0

VALIDATION_ERROR_422 = 422

TOTAL_SUCCESS_200 = 200

TOTAL_FAILURE_421 = 421

COIN = "COIN"

BILL = "BILL"

DIVISION_MULTIPLIER = 100

MULTIPLIER_FOR_DIVISION = 100

ERR_20_MAX_AMOUNT = "Amount exceeds the maximum withdrawal limit of 2000"
ERR_10_GREATER_THAN_ZERO = "Amount must be greater than zero"
ERR_TOO_MANY_COINS = "Too many coins"
ERR_INSUFFICIENT_FUNDS = "Insufficient funds. Max available amount:"

SETTINGS_MODE = os.getenv("SETTINGS_MODE", "redis")


def get_db_service():

    if SETTINGS_MODE == "redis":
        import redis
        inventory_service = RedisInventoryService(
            redis.StrictRedis(host='localhost', port=6379, db=0))
    else:
        from atm_service_json_file import JSONFileInventoryService
        inventory_service = JSONFileInventoryService()

    return inventory_service


inventory_service_settings = get_db_service()


def make_round(num):
    return round(num, int(len(str(MULTIPLIER_FOR_DIVISION)) - 1))


class ATMService:
    def __init__(self, inventory_service=None):
        self.inventory_service = inventory_service or inventory_service_settings

    def withdraw_money(self, amount, retries=3):
        if amount <= ZERO_MIN_AMOUNT:
            return ERR_10_GREATER_THAN_ZERO, VALIDATION_ERROR_422
        if amount > MAX_AMOUNT:
            return ERR_20_MAX_AMOUNT, VALIDATION_ERROR_422

        while retries > 0:
            try:
                self.inventory_service.acquire_lock()
                inventory_db = self.inventory_service.read_inventory()
                proposed_withdrawal, error, status_code, inventory = self._propose_withdrawal(inventory_db, amount)
                if error:
                    return error, status_code

                # update the actual inventory if all checks passed
                for denomination_type in [BILL, COIN]:
                    for denomination, num_notes in proposed_withdrawal[denomination_type].items():
                        inventory[denomination_type][denomination] -= num_notes
                inventory_db = self.inventory_to_db(inventory, inventory_db)
                self.inventory_service.write_inventory(inventory_db)
                return {"requested_amount": amount, "withdrawal": proposed_withdrawal}, TOTAL_SUCCESS_200
            except Exception as ex:
                return "total failure", TOTAL_FAILURE_421
            finally:
                self.inventory_service.release_lock()

    def refill_money(self, money, retries=3):
        while retries > 0:
            try:
                self.inventory_service.acquire_lock()
                inventory_db = self.inventory_service.read_inventory()
                inventory = self.inventory_from_bd(inventory_db)
                for denomination, amount in money.items():
                    denom_value = float(denomination)
                    if denom_value not in [200, 100, 20, 10, 1, 5, 0.1, 0.01]:
                        return f"Unknown denomination {denomination}", VALIDATION_ERROR_422

                    denom_type = BILL if denom_value >= 20 else COIN

                    if denom_value not in inventory[denom_type]:
                        inventory[denom_type][denom_value] = 0

                    inventory[denom_type][denom_value] += amount

                inventory_db = self.inventory_to_db(inventory, inventory_db)
                self.inventory_service.write_inventory(inventory_db)
                return {"refilled": money}, TOTAL_SUCCESS_200
            except Exception as ex:
                return "total failure", TOTAL_FAILURE_421
            finally:
                self.inventory_service.release_lock()

    def get_inventory(self, retries=3):
        while retries > 0:
            try:
                self.inventory_service.acquire_lock()
                inventory_db = self.inventory_service.read_inventory()
                inventory = self.inventory_from_bd(inventory_db)
                response = {
                    "result": {
                        "bills": {str(k): v for k, v in inventory[BILL].items() if v > 0},
                        "coins": {str(k): v for k, v in inventory[COIN].items() if v > 0}
                    }
                }
                return response
            except Exception as ex:
                return "total failure", TOTAL_FAILURE_421
            finally:
                self.inventory_service.release_lock()

    def restart(self, retries=3):
        while retries > 0:
            try:
                self.inventory_service.acquire_lock()
                self.inventory_service.restart()
            except Exception as ex:
                print(ex)
            finally:
                self.inventory_service.release_lock()
                return

    def get_total(self, retries=3):
        while retries > 0:
            try:
                self.inventory_service.acquire_lock()
                inventory_db = self.inventory_service.read_inventory()
                inventory = self.inventory_from_bd(inventory_db)
                total = sum(k * v for k, v in inventory[BILL].items()) + sum(
                    k * v for k, v in inventory[COIN].items())
                return {"total": total}
            except Exception as ex:
                return "total failure", TOTAL_FAILURE_421
            finally:
                self.inventory_service.release_lock()

    def perform_transaction(self, action, item_type, denomination, quantity, retries=3):
        while retries > 0:
            try:
                self.inventory_service.acquire_lock()
                inventory = self.inventory_service.read_inventory()

                denomination = float(denomination)
                quantity = int(quantity)

                if action == "put":
                    if item_type == BILL:
                        if denomination in inventory.BILL:
                            inventory.BILL[denomination] += quantity
                        else:
                            inventory.BILL[denomination] = quantity
                    elif item_type == COIN:
                        if denomination in inventory.COIN:
                            inventory.COIN[denomination] += quantity
                        else:
                            inventory.COIN[denomination] = quantity
                    self.inventory_service.write_inventory(inventory)
                    print(f"Put {quantity} of {denomination} {item_type.lower()}. New state: {inventory}")
                    return True

                elif action == "retrieve":
                    if item_type == BILL:
                        if denomination in inventory.BILL and inventory.BILL[denomination] >= quantity:
                            inventory.BILL[denomination] -= quantity
                        else:
                            return False
                    elif item_type == COIN:
                        if denomination in inventory.COIN and inventory.COIN[denomination] >= quantity:
                            inventory.COIN[denomination] -= quantity
                        else:
                            return False
                    self.inventory_service.write_inventory(inventory)
                    print(f"Retrieved {quantity} of {denomination} {item_type.lower()}. New state: {inventory}")
                    return True

                return False
            except Exception as e:
                print(f"Error performing transaction: {e}. Retrying...")
                retries -= 1
                time.sleep(0.1)
            finally:
                self.inventory_service.release_lock()
        return False

    def _propose_withdrawal(self, inventory_db: Inventory, amount: float):
        inventory = self.inventory_from_bd(inventory_db)

        proposed_withdrawal = {
            BILL: {},
            COIN: {}
        }
        total_coins = 0

        for denomination_type in [BILL, COIN]:
            denominations = sorted(inventory[denomination_type].keys(), reverse=True)
            for denomination in denominations:
                if amount == 0:
                    break
                num_notes = min(int((amount * DIVISION_MULTIPLIER) // (denomination * DIVISION_MULTIPLIER)),
                                inventory[denomination_type][denomination])
                if num_notes > 0:
                    if denomination_type == COIN:
                        total_coins += num_notes
                    # if total_coins > 50 and int(amount * DEVISION_MULTIPLIER) == 0:
                    if total_coins > 50:
                        return None, ERR_TOO_MANY_COINS, VALIDATION_ERROR_422, inventory
                    proposed_withdrawal[denomination_type][denomination] = num_notes
                    amount = make_round(amount - make_round(denomination * num_notes))

        if amount > 0:
            # available_amount = {
            #     "BILL": inventory["BILL"],
            #     "COIN": inventory["COIN"]
            # }
            # return None, f"{ERR_INSUFFICIENT_FUNDS} {available_amount}", 409 , inventory
            return None, f"{ERR_INSUFFICIENT_FUNDS} {0}", 409, inventory

        return proposed_withdrawal, None, TOTAL_SUCCESS_200, inventory

    def inventory_from_bd(self, inventory_db):
        inventory = {BILL: {}, COIN: {}}
        for k, v in inventory_db.BILL.items():
            inventory[BILL][k] = v
        for k, v in inventory_db.COIN.items():
            inventory[COIN][k] = v
        return inventory

    def inventory_to_db(self, inventory, inventory_db):
        inventory_db.BILL.clear()
        inventory_db.COIN.clear()

        for k, v in inventory['BILL'].items():
            inventory_db.BILL[k] = v
        for k, v in inventory['COIN'].items():
            inventory_db.COIN[k] = v
        return inventory_db
