from hiero_sdk_python import (
    Client, 
    AccountId, 
    PrivateKey, 
    TokenId, 
    TokenMintTransaction
)

# --- 1. Setup Client and Operator ---
client = Client()
operator_id = AccountId.from_string("0.0.7143910")
operator_key = PrivateKey.from_string("0x3cdfd578b5801141612ca7ac85779338f5cf88baeee49e9b73d11f9c42eb0bd0")
client.set_operator(operator_id, operator_key)

# --- 2. Define Transaction Variables ---

# This must be the PrivateKey for your token's supply
# !! REPLACE with your actual supply key !!
supply_key_string = "0xYOUR_SUPPLY_KEY_HEX_STRING" 
supply_key = PrivateKey.from_string(supply_key_string)

# This must be the TokenId you want to mint
# !! REPLACE with your actual token ID !!
token_id_string = "0.0.YOUR_TOKEN_ID"
token_id = TokenId.from_string(token_id_string)

# This must be a LIST of BYTES.
# This example will mint one NFT with the metadata "my_nft_meta".
metadata = [
    b"my_nft_meta"
]
# If you wanted to mint 3 NFTs in one transaction, it would look like this:
# metadata = [
#     b"metadata for NFT 1",
#     b"metadata for NFT 2",
#     b"metadata for NFT 3"
# ]


# --- 3. Build, Sign, and Execute the Transaction ---
print("Minting NFT...")
transaction = TokenMintTransaction(
    token_id=token_id,    # Pass the TokenId object
    metadata=metadata     # Pass the list of bytes
).freeze_with(client)

# Sign with the operator key (to pay for the transaction)
transaction.sign(operator_key)
# Sign with the token's supply key (to authorize minting)
transaction.sign(supply_key)

# Execute the transaction
response = transaction.execute(client)

# --- 4. (Recommended) Get the Receipt ---
receipt = response.get_receipt(client)
print(f"Token minting status: {receipt.status}")
print(f"Serial numbers of minted NFTs: {receipt.serials}")