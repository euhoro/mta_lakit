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

    def test_refill(self):
        self.client = TestClient(app)
        #self.client.post("/atm/restart")
        initial_inventory = self.client.get("/atm/inventory").json()
        #self.client.post("/atm/restart")
        bill_100 = 30
        num_5 = 30
        num_01 = 5
        bill_20 = 15
        refill_amount = {"0.1": num_01, "5": num_5, "20": bill_20, "100": bill_100}
        initial_inventory = self.client.get("/atm/inventory").json()
        result = self.client.post("/atm/refill", json={"money": refill_amount})
        updated_inventory = self.client.get("/atm/inventory").json()

        assert initial_inventory != updated_inventory
        assert initial_inventory['result']['bills']['100.0'] + bill_100 == updated_inventory['result']['bills']['100.0']
        assert initial_inventory['result']['bills']['20.0'] + bill_20 == updated_inventory['result']['bills']['20.0']
        assert initial_inventory['result']['coins']['0.1'] + num_01 == updated_inventory['result']['coins']['0.1']
        assert initial_inventory['result']['coins']['5.0'] + num_5 == updated_inventory['result']['coins']['5.0']


if __name__ == "__main__":
    unittest.main()
