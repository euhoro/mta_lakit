import unittest

from atm_repository_file import FileInventoryService
from atm_service import ATMService


class TestATMService(unittest.TestCase):
    def setUp(self):
        self.atm_service = ATMService()

    def test_atm_logic(self):
        amount, atm_service, total_before1 = self.assert_amount(100, 100, 1)
        total_after = atm_service.get_total()['total']
        self.assertEqual(total_before1, total_after + amount)

        atm_service.restart()
        total_before2 = atm_service.get_total()['total']
        self.assertEqual(total_before1, total_before2)

        # test2
        amount, atm_service, total_before1 = self.assert_amount(200, 200, 1)

        amount, atm_service, total_before1 = self.assert_amount(0.9, 0.1, 9, expected_type="COIN")
        pass

    def assert_amount(self, amount, expected_bill, expected_count, expected_type='BILL'):
        atm_service = ATMService()
        atm_service.restart()
        total_before1 = atm_service.get_total()['total']
        # amount = 100
        result = atm_service.withdraw_money(amount)
        assert result[0]['withdrawal'][expected_type][expected_bill] == expected_count
        return amount, atm_service, total_before1

    def test_atm_logic_max(self):
        atm_service = ATMService()
        total_before = atm_service.get_total()['total']
        amount = 2000
        atm_service.withdraw_money(amount)
        # total_after = atm_service.get_total()['total']
        # self.assertAlmostEqual(total_before, total_after + amount, places=2)

    # todo:
    def test_atm_logic_too_many_coins(self):
        atm_service = ATMService()
        total_before = atm_service.get_total()['total']
        # for i in range(4):
        #     amount = 0.9

        total1 = atm_service.get_total()
        result = atm_service.withdraw_money(0.9)  # should remain 3 of 0.1

        total2 = atm_service.get_total()
        total = atm_service.get_inventory()
        result = atm_service.withdraw_money(21.61)

        total3 = atm_service.get_total()
        assert total2 == total3  # because we did not took money
        pass
        # total_after = atm_service.get_total()['total']
        # self.assertAlmostEqual(total_before, total_after + amount, places=2)


if __name__ == "__main__":
    unittest.main()
