from threading import Lock


class ATMService:
    def __init__(self):
        self.inventory = {
            "BILL": {200: 7, 100: 4, 20: 15},
            "COIN": {10: 10, 1: 1000, 5: 1, 0.1: 12, 0.01: 21}
        }
        self.inventory_lock = Lock()

    def withdraw_money(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        original_amount = amount
        withdrawal = {
            "BILL": {},
            "COIN": {}
        }

        with self.inventory_lock:
            for denomination_type in ["BILL", "COIN"]:
                denominations = sorted(self.inventory[denomination_type].keys(), reverse=True)
                for denomination in denominations:
                    if amount == 0:
                        break
                    num_notes = min(amount // denomination, self.inventory[denomination_type][denomination])
                    if num_notes > 0:
                        withdrawal[denomination_type][denomination] = int(num_notes)
                        amount -= denomination * num_notes
                        self.inventory[denomination_type][denomination] -= int(num_notes)
                        amount = round(amount, 2)

            if amount > 0:
                raise ValueError("Insufficient funds or denominations to fulfill the request")

        return {"requested_amount": original_amount, "withdrawal": withdrawal}

    def refill_money(self, money):
        with self.inventory_lock:
            for denomination, amount in money.items():
                denom_value = float(denomination)
                if denom_value >= 1:
                    denom_type = "BILL"
                else:
                    denom_type = "COIN"

                if denom_value not in self.inventory[denom_type]:
                    self.inventory[denom_type][denom_value] = 0

                self.inventory[denom_type][denom_value] += amount

        return {"refilled": money}

    def get_inventory(self):
        with self.inventory_lock:
            response = {
                "result": {
                    "bills": {str(k): v for k, v in self.inventory["BILL"].items() if v > 0},
                    "coins": {str(k): v for k, v in self.inventory["COIN"].items() if v > 0}
                }
            }
        return response

    def get_total(self):
        with self.inventory_lock:
            total = sum(k * v for k, v in self.inventory["BILL"].items()) + sum(
                k * v for k, v in self.inventory["COIN"].items())
        return {"total": total}
