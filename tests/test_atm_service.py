import unittest
from atm_service import ATMService


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

    def test_atm_logic_max(self):
        atm_service = ATMService()
        total_before = atm_service.get_total()['total']
        amount = 2000
        atm_service.withdraw_money(amount)
        # total_after = atm_service.get_total()['total']
        # self.assertAlmostEqual(total_before, total_after + amount, places=2)

    # todo:
    # def test_atm_logic_too_many_coins(self):
    #     atm_service = ATMService()
    #     total_before = atm_service.get_total()['total']
    #     for i in range(4):
    #         amount = 0.9
    #         atm_service.withdraw_money(amount)
    #
    #     atm_service.withdraw_money(21.61)
    #     # total_after = atm_service.get_total()['total']
    #     # self.assertAlmostEqual(total_before, total_after + amount, places=2)


if __name__ == "__main__":
    unittest.main()
