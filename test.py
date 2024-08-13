import requests

token_contract = "0xE261D618a959aFfFd53168Cd07D12E37B26761db"

print("ping -> ", requests.get("http://localhost:8080/ping").text)

response = requests.get(
    "http://localhost:8080/get_balance",
    json={
        "address": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
    }
)

print(response.json())

response = requests.get(
"http://localhost:8080/get_balance_batch",
    json={
        "addresses": [
            "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
        ],
        "token_contract": token_contract
    }
)

print(response.json())

response = requests.get(
"http://localhost:8080/get_token_top_holders",
    json={
        "token_address": token_contract
    }
)
print(response.json())

response = requests.get(
    "http://localhost:8080/get_token_top_holders_and_ts",
    json={
        "token_address": token_contract
    }
)
print(response.json())
