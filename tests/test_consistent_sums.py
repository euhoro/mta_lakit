import unittest
import requests
from threading import Thread


class TestATM(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000/atm"

    #todo : re-do this
    # def test_total_with_multithreaded_withdrawals(self):
    #     # Get initial total
    #     response = requests.get(f"{self.base_url}/total")
    #     self.assertEqual(response.status_code, 200)
    #     initial_total = response.json()["total"]
    #
    #     # Create threads for withdrawal
    #     num_threads = 100
    #     withdrawal_amount = 0.01
    #     total_withdrawn = 0
    #
    #     def withdraw():
    #         nonlocal total_withdrawn
    #         response = requests.post(f"{self.base_url}/withdrawal", json={"amount": withdrawal_amount})
    #         if response.status_code == 200:
    #             with self.withdrawal_lock:
    #                 total_withdrawn += withdrawal_amount
    #
    #     threads = []
    #     for _ in range(num_threads):
    #         thread = Thread(target=withdraw)
    #         threads.append(thread)
    #         thread.start()
    #
    #     for thread in threads:
    #         thread.join()
    #
    #     # Get total after withdrawals
    #     response = requests.get(f"{self.base_url}/total")
    #     self.assertEqual(response.status_code, 200)
    #     final_total = response.json()["total"]
    #
    #     # Checks initial total equals the final total plus the money that was taken
    #     self.assertAlmostEqual(initial_total, final_total + total_withdrawn, places=2)


    # def test_total_with_multithreaded_withdrawals(self):
    #     # get total
    #     response = requests.get(f"{self.base_url}/total")
    #     self.assertEqual(response.status_code, 200)
    #     initial_total = response.json()["total"]
    #
    #     # create threads with amount
    #     num_threads = 100
    #     withdrawal_amount = 0.01
    #     total_withdrawn = num_threads * withdrawal_amount
    #
    #     # request withdrawal request
    #     def withdraw():
    #         requests.post(f"{self.base_url}/withdrawal", json={"amount": withdrawal_amount})
    #
    #     # start all threads
    #     threads = []
    #     for _ in range(num_threads):
    #         thread = Thread(target=withdraw)
    #         threads.append(thread)
    #         thread.start()
    #
    #     # wait for completion
    #     for thread in threads:
    #         thread.join()
    #
    #     # get total after everybody receives money
    #     response = requests.get(f"{self.base_url}/total")
    #     self.assertEqual(response.status_code, 200)
    #     final_total = response.json()["total"]
    #
    #     # checks initial total equals the final total plus the money that was taken
    #     #self.assertAlmostEqual(initial_total, final_total + total_withdrawn, places=2)
    #     self.assertEqual(initial_total, final_total + total_withdrawn)


if __name__ == "__main__":
    unittest.main()
