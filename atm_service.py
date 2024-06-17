from threading import Lock

#from atm_repository_file import FileInventoryService
#from atm_repository_mem import InMemoryInventoryService
from atm_repository_sqllite import SQLiteInventoryService

DEVISION_MULTIPLIER = 100

MULTIPLIER_FOR_DIVISION = 100

ERR_20_MAX_AMOUNT = "Amount exceeds the maximum withdrawal limit of 2000"
ERR_10_GREATER_THAN_ZERO = "Amount must be greater than zero"
ERR_TOO_MANY_COINS = "Too many coins"
ERR_INSUFFICIENT_FUNDS = "Insufficient funds. Max available amount:"


class ATMService:

    def __init__(self, inventory_service=None):
        self.inventory_lock = Lock()
        #self.inventory_service = inventory_service or InMemoryInventoryService()
        #self.inventory_service = inventory_service or FileInventoryService()
        self.inventory_service = inventory_service or SQLiteInventoryService()
        self.inventory = self.inventory_service.read_inventory()

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
                num_notes = min(int((amount * DEVISION_MULTIPLIER) // (denomination *DEVISION_MULTIPLIER)), self.inventory[denomination_type][denomination])
                if num_notes > 0:
                    if denomination_type == "COIN":
                        total_coins += num_notes
                    if total_coins > 50 and int(amount * DEVISION_MULTIPLIER) == 0:
                        return None, ERR_TOO_MANY_COINS, 422
                    proposed_withdrawal[denomination_type][denomination] = num_notes
                    amount = self.make_round(amount - self.make_round(denomination * num_notes))

        if amount > 0:
            available_amount = {
                "BILL": self.inventory["BILL"],
                "COIN": self.inventory["COIN"]
            }
            return None, f"{ERR_INSUFFICIENT_FUNDS} {available_amount}", 409

        return proposed_withdrawal, None, 200

    def make_round(self, num):
        return round(num, int(len(str(MULTIPLIER_FOR_DIVISION)) - 1))

    def withdraw_money(self, amount):
        if amount <= 0:
            return ERR_10_GREATER_THAN_ZERO, 422
        if amount > 2000:
            return ERR_20_MAX_AMOUNT, 422

        with self.inventory_lock:
            self.inventory = self.inventory_service.read_inventory()
            proposed_withdrawal, error, status_code = self._propose_withdrawal(amount)
            if error:
                return error, status_code

            # Update the actual inventory if all checks passed
            for denomination_type in ["BILL", "COIN"]:
                for denomination, num_notes in proposed_withdrawal[denomination_type].items():
                    self.inventory[denomination_type][denomination] -= num_notes

            self.inventory_service.write_inventory(self.inventory)
            return {"requested_amount": amount, "withdrawal": proposed_withdrawal}, 200

    def refill_money(self, money):
        with self.inventory_lock:
            self.inventory = self.inventory_service.read_inventory()
            for denomination, amount in money.items():
                denom_value = float(denomination)
                if denom_value not in [200, 100, 20, 10, 1, 5, 0.1, 0.01]:
                    return f"Unknown denomination {denomination}", 422

                denom_type = "BILL" if denom_value >= 20 else "COIN"

                if denom_value not in self.inventory[denom_type]:
                    self.inventory[denom_type][denom_value] = 0

                self.inventory[denom_type][denom_value] += amount

            self.inventory_service.write_inventory(self.inventory)
            return {"refilled": money}, 200

    def get_inventory(self):
        with self.inventory_lock:
            self.inventory = self.inventory_service.read_inventory()
            response = {
                "result": {
                    "bills": {str(k): v for k, v in self.inventory["BILL"].items() if v > 0},
                    "coins": {str(k): v for k, v in self.inventory["COIN"].items() if v > 0}
                }
            }
        return response

    def get_total(self):
        with self.inventory_lock:
            self.inventory = self.inventory_service.read_inventory()
            total = sum(k * v for k, v in self.inventory["BILL"].items()) + sum(
                k * v for k, v in self.inventory["COIN"].items())
        return {"total": total}

    def restart(self):
        with self.inventory_lock:
            self.inventory_service.restart()
