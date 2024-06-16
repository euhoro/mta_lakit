import unittest
from atm_service import ATMService
from threading import Thread


class TestATMService(unittest.TestCase):
    def setUp(self):
        self.atm_service = ATMService()

    def test_atm_logic(self):
        atm_service = ATMService()
        total_before = atm_service.get_total()['total']
        amount = 100
        atm_service.withdraw_money(amount)
        total_after = atm_service.get_total()['total']
        self.assertAlmostEqual(total_before, total_after + amount, places=2)



if __name__ == "__main__":
    unittest.main()
