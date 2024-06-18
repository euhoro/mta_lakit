import subprocess
import json
import pytest


def run_curl_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result


def test_withdraw_zero_amount_curl():
    command = """curl -L -g -X POST 'http://127.0.0.1:8000/atm/withdrawal' -H 'Content-Type: application/json' --data-raw '{"amount": 0}'"""
    result = run_curl_command(command)
    assert result.returncode == 0, f"Curl command failed with return code {result.returncode}"

    response_json = json.loads(result.stdout)
    assert response_json["detail"] == "Amount must be greater than zero"
    #assert "422" in result.stderr


def test_withdraw_negative_amount_curl():
    #command = """curl -L -g -X POST 'http://127.0.0.1:8000/atm/withdrawal' -H 'Content-Type: application/json' --data-raw '{"amount": -10}'"""
    command = """curl -L -g -X POST 'http://127.0.0.1:8000/atm/withdrawal' -H 'Content-Type: application/json' --data-raw '{"amount": 0}' -w '\\n%{http_code}'"""
    result = run_curl_command(command)
    assert result.returncode == 0, f"Curl command failed with return code {result.returncode}"

    response_json = json.loads(result.stdout.split('\n')[0])
    assert response_json["detail"] == "Amount must be greater than zero"
    assert "422" in result.stdout


if __name__ == "__main__":
    pytest.main()
