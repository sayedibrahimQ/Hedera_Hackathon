
from hedera import (
    ContractCreateFlow,
    ContractExecuteTransaction,
    ContractFunctionParameters,
)

from nilefi.apps.blockchain.hedera_client import client, DEFAULT_GAS
from nilefi.apps.blockchain.constants import (
    ASSET_TOKENIZATION_CONTRACT_ID,
    RENTAL_AGREEMENT_CONTRACT_ID,
)

def deploy_contracts():
    """Deploys the asset tokenization and rental agreement contracts.

    Returns:
        A tuple containing the receipt and record of the deployment transaction.
    """
    # Compile the contracts (assuming you have a compilation script)
    # ...

    # Deploy the asset tokenization contract
    asset_contract_receipt, asset_contract_record = _deploy_contract(
        "AssetTokenization.json"
    )

    # Deploy the rental agreement contract
    rental_contract_receipt, rental_contract_record = _deploy_contract(
        "RentalAgreement.json"
    )

    return (
        (asset_contract_receipt, asset_contract_record),
        (rental_contract_receipt, rental_contract_record),
    )


def _deploy_contract(bytecode_path):
    """Helper function to deploy a single contract.

    Args:
        bytecode_path: The path to the contract's bytecode file.

    Returns:
        A tuple containing the receipt and record of the deployment transaction.
    """
    with open(bytecode_path, "rb") as f:
        bytecode = f.read()

    tx = (
        ContractCreateFlow()
        .setBytecode(bytecode)
        .setGas(DEFAULT_GAS)
        .execute(client)
    )

    return tx.getReceipt(client), tx.getRecord(client)


def tokenize_asset(property_id, owner, value):
    """Tokenizes a real estate asset.

    Args:
        property_id: The unique identifier of the property.
        owner: The Hedera account ID of the property owner.
        value: The value of the property.

    Returns:
        The transaction receipt.
    """
    tx = (
        ContractExecuteTransaction()
        .setContractId(ASSET_TOKENIZATION_CONTRACT_ID)
        .setGas(DEFAULT_GAS)
        .setFunction(
            "tokenize",
            ContractFunctionParameters()
            .addString(property_id)
            .addAddress(owner.toSolidityAddress())
            .addUint256(value),
        )
        .execute(client)
    )

    return tx.getReceipt(client)


def create_rental_agreement(property_id, tenant, rent_amount, duration):
    """Creates a rental agreement for a property.

    Args:
        property_id: The ID of the property.
        tenant: The Hedera account ID of the tenant.
        rent_amount: The monthly rent amount.
        duration: The duration of the rental agreement in months.

    Returns:
        The transaction receipt.
    """
    tx = (
        ContractExecuteTransaction()
        .setContractId(RENTAL_AGREEMENT_CONTRACT_ID)
        .setGas(DEFAULT_GAS)
        .setFunction(
            "createAgreement",
            ContractFunctionParameters()
            .addString(property_id)
            .addAddress(tenant.toSolidityAddress())
            .addUint256(rent_amount)
            .addUint256(duration),
        )
        .execute(client)
    )

    return tx.getReceipt(client)
