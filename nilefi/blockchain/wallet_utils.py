
from hedera import (
    PrivateKey,
    PublicKey,
    AccountCreateTransaction,
    Hbar,
)

from .hedera_client import client

def create_account():
    """Creates a new Hedera account with a new key pair.

    Returns:
        A tuple containing the new private key, new public key, and new account ID.
    """
    # Generate a new key pair
    private_key = PrivateKey.generateED25519()
    public_key = private_key.getPublicKey()

    # Create a new account
    tx = (
        AccountCreateTransaction()
        .setKey(public_key)
        .setInitialBalance(Hbar.fromTinybars(1000))  # Initial balance for the new account
        .execute(client)
    )

    # Get the new account ID from the receipt
    receipt = tx.getReceipt(client)
    new_account_id = receipt.accountId

    return private_key, public_key, new_account_id
