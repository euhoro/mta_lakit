from pydantic import BaseModel
from typing import Dict


class WithdrawalRequest(BaseModel):
    amount: float


class RefillRequest(BaseModel):
    money: Dict[str, int]


class InventoryResponse(BaseModel):
    result: Dict[str, Dict[str, int]]
