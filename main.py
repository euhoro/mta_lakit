from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn

from atm_repository_mem import InMemoryInventoryService
from atm_repository_file import FileInventoryService
from atm_service import ATMService

app = FastAPI()

#atm_service = ATMService(InMemoryInventoryService())
atm_service = ATMService()


class WithdrawalRequest(BaseModel):
    amount: float


class RefillRequest(BaseModel):
    money: Dict[str, int]


class InventoryResponse(BaseModel):
    result: Dict[str, Dict[str, int]]


@app.post("/atm/withdrawal")
def withdraw_money(request: WithdrawalRequest):
    result, status_code = atm_service.withdraw_money(request.amount)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result)
    return result


@app.post("/atm/refill")
def refill_money(request: RefillRequest):
    result, status_code = atm_service.refill_money(request.money)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result)
    return result


@app.get("/atm/inventory", response_model=InventoryResponse)
def get_inventory():
    result = atm_service.get_inventory()
    return result


@app.get("/atm/total")
def get_total():
    result = atm_service.get_total()
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
