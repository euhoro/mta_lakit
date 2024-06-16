from fastapi import FastAPI, HTTPException

from models import WithdrawalRequest, RefillRequest, InventoryResponse

import uvicorn

C_COIN = "COIN"

C_BILL = "BILL"

app = FastAPI()

# todo - replace with db service
inventory = {
    C_BILL: {200: 7, 100: 4, 20: 15},
    C_COIN: {10: 10, 1: 10, 5: 1, 0.1: 12, 0.01: 21}
}


@app.post("/atm/withdrawal")
def withdraw_money(request: WithdrawalRequest):
    amount = request.amount
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    original_amount = amount
    withdrawal = {
        C_BILL: {},
        C_COIN: {}
    }

    # todo implement get_cash
    amount = get_cash(amount, withdrawal)

    if amount > 0:
        raise HTTPException(status_code=400, detail="Insufficient funds or denominations to fulfill the request")

    return {"requested_amount": original_amount, "withdrawal": withdrawal}


def get_cash(amount, withdrawal):
    for denomination_type in [C_BILL, C_COIN]:
        denominations = sorted(inventory[denomination_type].keys(), reverse=True)
        for denomination in denominations:
            if amount == 0:
                break
            num_notes = min(amount // denomination, inventory[denomination_type][denomination])
            if num_notes > 0:
                withdrawal[denomination_type][denomination] = int(num_notes)
                amount -= denomination * num_notes
                inventory[denomination_type][denomination] -= int(num_notes)
                amount = round(amount, 2)
    return amount


@app.post("/atm/refill")
def refill_money(request: RefillRequest):
    for denomination, amount in request.money.items():
        denom_value = float(denomination)
        if denom_value >= 1:
            denom_type = C_BILL
        else:
            denom_type = C_COIN

        if denom_value not in inventory[denom_type]:
            inventory[denom_type][denom_value] = 0

        inventory[denom_type][denom_value] += amount

    return {"refilled": request.money}


@app.get("/atm/inventory", response_model=InventoryResponse)
def get_inventory():
    response = {
        "result": {
            "bills": {str(k): v for k, v in inventory[C_BILL].items() if v > 0},
            "coins": {str(k): v for k, v in inventory[C_COIN].items() if v > 0}
        }
    }
    return response


@app.get("/atm/total")
def get_total():
    total = sum(k * v for k, v in inventory["BILL"].items()) + sum(k * v for k, v in inventory["COIN"].items())
    return {"total": total}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
