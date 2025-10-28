
from nilefi.apps.blockchain.contracts import (
    tokenize_asset,
    create_rental_agreement,
)
from nilefi.apps.blockchain.ofd_integration import get_property_data
from nilefi.apps.blockchain.wallet_utils import create_account


def tokenize_real_estate_asset(property_id, owner_account_id):
    """Tokenizes a real estate asset after verifying ownership through OFD.

    Args:
        property_id: The ID of the property to tokenize.
        owner_account_id: The Hedera account ID of the property owner.

    Returns:
        The transaction receipt of the tokenization.
    """
    # 1. Fetch property data from OFD
    property_data = get_property_data(property_id)

    # 2. Verify ownership (add your verification logic here)
    # For example, check if the owner in OFD matches the provided owner_account_id

    # 3. Tokenize the asset on Hedera
    receipt = tokenize_asset(
        property_id, owner_account_id, property_data["value"]
    )

    return receipt


def setup_rental_agreement(
    property_id, tenant_account_id, rent_amount, duration
):
    """Creates and manages a rental agreement on the Hedera network.

    Args:
        property_id: The ID of the property.
        tenant_account_id: The Hedera account ID of the tenant.
        rent_amount: The monthly rent amount.
        duration: The duration of the rental agreement in months.

    Returns:
        The transaction receipt of the rental agreement creation.
    """
    # Create the rental agreement on the smart contract
    receipt = create_rental_agreement(
        property_id, tenant_account_id, rent_amount, duration
    )

    return receipt
