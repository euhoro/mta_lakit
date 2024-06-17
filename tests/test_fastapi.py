import unittest

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


#
# def test_total_with_multithreaded_withdrawals():
#     response = client.get("/atm/total")
#     assert response.status_code == 200
#     initial_total = response.json()["total"]
#
#     num_threads = 100
#     withdrawal_amount = 1
#     total_withdrawn = num_threads * withdrawal_amount
#
#     def withdraw():
#         try:
#             client.post("/atm/withdrawal", json={"amount": withdrawal_amount})
#         except Exception as e:
#             print(e)
#
#     import threading
#     threads = []
#     for _ in range(num_threads):
#         thread = threading.Thread(target=withdraw)
#         threads.append(thread)
#         thread.start()
#
#     for thread in threads:
#         thread.join()
#
#     response = client.get("/atm/total")
#     assert response.status_code == 200
#     final_total = response.json()["total"]
#     assert round(initial_total, 2) == round(final_total + total_withdrawn, 2)

def test_refill():
    refill_amount = {"0.1": 5, "5": 30, "20": 15, "100": 30}
    initial_inventory = client.get("/atm/inventory").json()
    client.post("/atm/refill", json={"money": refill_amount})
    updated_inventory = client.get("/atm/inventory").json()

    assert initial_inventory != updated_inventory


def test_withdraw_zero_amount():
    response = client.post("/atm/withdrawal", json={"amount": 3000})
    assert response.status_code == 422
    assert response.json()["detail"] == "Amount must be max 2000"


def test_withdraw_negative_amount():
    response = client.post("/atm/withdrawal", json={"amount": -10})
    assert response.status_code == 422
    assert response.json()["detail"] == "Amount must be greater than zero"

#todo:
# V. If there is not enough money (bills or coins) in the ATM return http status 409 (conflict) with the max
# current amount available for the withdrawal for each denomination.
#
# VI. If the calculated results has more than 50 coins, the server should fail on ‘too many coins’ and
# respond with status 422 ((Unprocessable Entity)

# If an unknown bill/coin is provided then the server should respond with status 422 (Unprocessable
# Entity) and appropriate message


if __name__ == "__main__":
    unittest.main()
