
from hedera import (
    AccountId,
    ContractId,
)

# Hedera account credentials
OPERATOR_ID = AccountId.fromString("YOUR_OPERATOR_ID")
OPERATOR_KEY = "YOUR_OPERATOR_PRIVATE_KEY"

# Deployed contract IDs
ASSET_TOKENIZATION_CONTRACT_ID = ContractId.fromString("YOUR_ASSET_TOKENIZATION_CONTRACT_ID")
RENTAL_AGREEMENT_CONTRACT_ID = ContractId.fromString("YOUR_RENTAL_AGREEMENT_CONTRACT_ID")

# OFD API credentials (replace with your actual credentials)
OFD_API_KEY = "YOUR_OFD_API_KEY"
OFD_API_SECRET = "YOUR_OFD_API_SECRET"
