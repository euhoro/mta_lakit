import unittest

from atm_repository_file import FileInventoryService
from atm_service import ATMService, ERR_INSUFFICIENT_FUNDS, ERR_TOO_MANY_COINS
from fastapi.testclient import TestClient

from main import app


class TestATMService(unittest.TestCase):
    def setUp(self):
        #self.client = TestClient(app)
        #self.client.post("/atm/restart")
        pass

    # def test_too_many_coins(self):
    #     #response = self.client.post("/atm/withdrawal", json={"amount": 0.9})
    #     #response = self.client.post("/atm/withdrawal", json={"amount": 0.4})
    #
    #     refill_amount = {"0.01": 1000}
    #     initial_inventory = self.client.get("/atm/inventory").json()
    #     self.client.post("/atm/refill", json={"money": refill_amount})
    #     updated_inventory = self.client.get("/atm/inventory").json()
    #
    #
    #     response = self.client.post("/atm/withdrawal", json={"amount": 0.9})
    #     response = self.client.post("/atm/withdrawal", json={"amount": 0.1})
    #     response = self.client.post("/atm/withdrawal", json={"amount": 0.1})
    #     response = self.client.post("/atm/withdrawal", json={"amount": 21.61})
    #     #response = self.client.post("/atm/withdrawal", json={"amount": 21.61})
    #
    #     assert response.status_code == 422
    #     assert ERR_TOO_MANY_COINS in response.json()["detail"]

    def test_not_enough(self):
        self.client = TestClient(app)
        response = self.client.post("/atm/withdrawal", json={"amount": 1000})
        response = self.client.post("/atm/withdrawal", json={"amount": 1000})
        response = self.client.post("/atm/withdrawal", json={"amount": 1000})
        assert response.status_code == 409
        assert ERR_INSUFFICIENT_FUNDS in response.json()["detail"]

    def test_max(self):
        self.client = TestClient(app)
        response = self.client.post("/atm/withdrawal", json={"amount": 3000})
        assert response.status_code == 422
        assert response.json()["detail"] == "Amount exceeds the maximum withdrawal limit of 2000"

    def test_bad(self):
        self.client = TestClient(app)
        response = self.client.post("/atm/withdrawal", json={})
        assert response.status_code == 422
        assert response.json()["detail"] == "Amount exceeds the maximum withdrawal limit of 2000"



if __name__ == "__main__":
    unittest.main()
