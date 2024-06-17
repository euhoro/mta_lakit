import fcntl
import json
import os
from threading import Lock

INVENTORY_FILE = 'inventory.json'
MULTIPLIER_FOR_DIVISION = 100

ERR_20_MAX_AMOUNT = "Amount exceeds the maximum withdrawal limit of 2000"
ERR_10_GREATER_THAN_ZERO = "Amount must be greater than zero"
ERR_TOO_MANY_COINS = "Too many coins"
ERR_INSUFFICIENT_FUNDS = "Insufficient funds. Max available amount:"


class ATMService:
    def __init__(self):
        self.inventory_lock = Lock()
        if not os.path.exists(INVENTORY_FILE):
            self.inventory = {
                "BILL": {200: 7, 100: 4, 20: 15},
                "COIN": {10: 10, 1: 10, 5: 1, 0.1: 12, 0.01: 21}
            }
            self._write_inventory_to_file()
        else:
            self.inventory = self._read_inventory_from_file()

    def _read_inventory_from_file(self):
        with open(INVENTORY_FILE, 'r') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            inventory = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)

        self.inventory = self.reformat_inventory(inventory)
        return self.inventory

    def reformat_inventory(self, inventory):
        inventory["BILL"] = {int(k): v for k, v in inventory["BILL"].items()}
        inventory["COIN"] = {float(k): v for k, v in inventory["COIN"].items()}
        return inventory

    def _write_inventory_to_file(self):
        with open(INVENTORY_FILE, 'w') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            json.dump(self.reformat_inventory(self.inventory), file)
            fcntl.flock(file, fcntl.LOCK_UN)

    def _propose_withdrawal(self, amount):
        proposed_withdrawal = {
            "BILL": {},
            "COIN": {}
        }
        total_coins = 0

        for denomination_type in ["BILL", "COIN"]:
            denominations = sorted(self.inventory[denomination_type].keys(), reverse=True)
            for denomination in denominations:
                if amount == 0:
                    break
                num_notes = min(int(amount // denomination), self.inventory[denomination_type][denomination])
                if num_notes > 0:
                    if denomination_type == "COIN":
                        total_coins += num_notes
                    if total_coins > 50:
                        return None, ERR_TOO_MANY_COINS, 422
                    proposed_withdrawal[denomination_type][denomination] = num_notes
                    amount -= denomination * num_notes

        if amount > 0:
            available_amount = {
                "BILL": self.inventory["BILL"],
                "COIN": self.inventory["COIN"]
            }
            return None, f"{ERR_INSUFFICIENT_FUNDS} {available_amount}", 409

        return proposed_withdrawal, None, 200

    def withdraw_money(self, amount):
        if amount <= 0:
            return ERR_10_GREATER_THAN_ZERO, 422
        if amount > 2000:
            return ERR_20_MAX_AMOUNT, 422

        with self.inventory_lock:
            self.inventory = self._read_inventory_from_file()
            proposed_withdrawal, error, status_code = self._propose_withdrawal(amount)
            if error:
                return error, status_code

            # Update the actual inventory if all checks passed
            for denomination_type in ["BILL", "COIN"]:
                for denomination, num_notes in proposed_withdrawal[denomination_type].items():
                    self.inventory[denomination_type][denomination] -= num_notes

            self._write_inventory_to_file()
            return {"requested_amount": amount, "withdrawal": proposed_withdrawal}, 200

    def refill_money(self, money):
        with self.inventory_lock:
            self.inventory = self._read_inventory_from_file()
            for denomination, amount in money.items():
                denom_value = float(denomination)
                if denom_value not in [200, 100, 20, 10, 1, 5, 0.1, 0.01]:
                    return f"Unknown denomination {denomination}", 422

                denom_type = "BILL" if denom_value >= 1 else "COIN"

                if denom_value not in self.inventory[denom_type]:
                    self.inventory[denom_type][denom_value] = 0

                self.inventory[denom_type][denom_value] += amount

            self._write_inventory_to_file()
            return {"refilled": money}, 200

    def get_inventory(self):
        with self.inventory_lock:
            self.inventory = self._read_inventory_from_file()
            response = {
                "result": {
                    "bills": {str(k): v for k, v in self.inventory["BILL"].items() if v > 0},
                    "coins": {str(k): v for k, v in self.inventory["COIN"].items() if v > 0}
                }
            }
        return response

    def get_total(self):
        with self.inventory_lock:
            self.inventory = self._read_inventory_from_file()
            total = sum(k * v for k, v in self.inventory["BILL"].items()) + sum(
                k * v for k, v in self.inventory["COIN"].items())
        return {"total": total}
