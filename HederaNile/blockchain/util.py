import requests

def get_public_key_from_hedera(account_id):
    url = f"https://testnet.mirrornode.hedera.com/api/v1/accounts/{account_id}"
    response = requests.get(url)
    print(response.json()["key"]["key"])
    return response.json()["key"]["key"]

