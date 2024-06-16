from fastapi import FastAPI, HTTPException

from atm_service import ATMService
from models import WithdrawalRequest, RefillRequest, InventoryResponse

import uvicorn

C_COIN = "COIN"

C_BILL = "BILL"

app = FastAPI()

atm_service = ATMService()


@app.post("/atm/withdrawal")
def withdraw_money(request: WithdrawalRequest):
    try:
        result = atm_service.withdraw_money(request.amount)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/atm/refill")
def refill_money(request: RefillRequest):
    result = atm_service.refill_money(request.money)
    return result


@app.get("/atm/inventory", response_model=InventoryResponse)
def get_inventory():
    result = atm_service.get_inventory()
    return result


@app.get("/atm/total")
def get_total():
    result = atm_service.get_total()
    return result


# todo : remove this when deploy to prod
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
