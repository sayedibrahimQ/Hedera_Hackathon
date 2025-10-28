
from hedera import (
    Client,
    Hbar,
    TransactionReceiptQuery,
)

from nilefi.apps.blockchain.constants import OPERATOR_ID, OPERATOR_KEY

# Configure the Hedera client
client = Client.forTestnet()  # Or Client.forMainnet()
client.setOperator(OPERATOR_ID, OPERATOR_KEY)

# Define gas limits for contract interactions
DEFAULT_GAS = 100_000


def get_transaction_receipt(transaction_id):
    """Queries for the receipt of a given transaction.

    Args:
        transaction_id: The ID of the transaction to query.

    Returns:
        The transaction receipt.
    """
    return TransactionReceiptQuery().setTransactionId(transaction_id).execute(client)
