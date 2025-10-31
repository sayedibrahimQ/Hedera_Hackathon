"""
Custodial Escrow Service for NileFi.
Manages escrow account for holding investor funds until milestone verification.
"""

import time
from decimal import Decimal
from typing import Optional
from django.conf import settings

try:
    from hiero_sdk_python import (
        Client,
        PrivateKey,
        AccountId,
        Hbar,
        CryptoGetAccountBalanceQuery,
        TransferTransaction,
    )
    HIERO_AVAILABLE = True
except ImportError:
    HIERO_AVAILABLE = False
    print("Warning: hiero-sdk-python not available. Using mock implementation.")


class EscrowService:
    """
    Custodial escrow service for managing funds.
    In MVP, uses a custodial account controlled by the platform.
    Can be upgraded to smart contract escrow later.
    """
    
    def __init__(self):
        self.network = settings.HEDERA_NETWORK
        self.operator_id = settings.HEDERA_OPERATOR_ID
        self.operator_key = settings.HEDERA_OPERATOR_KEY
        self.escrow_account_id = settings.HEDERA_ESCROW_ACCOUNT_ID
        
        if HIERO_AVAILABLE and self.operator_id and self.operator_key:
            self.client = self._init_client()
        else:
            self.client = None
            print("Escrow: Running in mock mode")
    
    def _init_client(self):
        """Initialize Hedera client"""
        try:
            if self.network == 'testnet':
                client = Client.forTestnet()
            elif self.network == 'mainnet':
                client = Client.forMainnet()
            else:
                raise ValueError(f"Unknown network: {self.network}")
            
            operator_key = PrivateKey.fromStringED25519(self.operator_key)
            operator_account = AccountId.fromString(self.operator_id)
            
            client.setOperator(operator_account, operator_key)
            return client
        except Exception as e:
            print(f"Error initializing Hedera client: {e}")
            return None
    
    def transfer_to_escrow(
        self,
        from_account_id: str,
        amount: Decimal
    ) -> Optional[str]:
        """
        Accept transfer from investor to escrow account.
        Note: In practice, the investor initiates this from their wallet.
        This method is for backend verification and recording.
        
        Returns transaction hash if successful.
        """
        if not self.client:
            return self._mock_transaction_hash()
        
        try:
            # In practice, the investor initiates this transaction
            # This is a placeholder for backend-initiated transfers if needed
            print(f"Transfer to escrow: {from_account_id} -> {self.escrow_account_id}: {amount} HBAR")
            
            # For MVP, we primarily verify transactions initiated by users
            # Return mock hash for development
            return self._mock_transaction_hash()
            
        except Exception as e:
            print(f"Error in escrow transfer: {e}")
            return None
    
    def release_from_escrow(
        self,
        to_account_id: str,
        amount: Decimal,
        memo: str = ""
    ) -> Optional[str]:
        """
        Release funds from escrow to recipient (startup account).
        Called when milestone is verified.
        
        Args:
            to_account_id: Hedera account ID of recipient
            amount: Amount to release in HBAR
            memo: Transaction memo
        
        Returns:
            Transaction hash if successful
        """
        if not self.client:
            return self._mock_transaction_hash()
        
        try:
            # Create transfer transaction
            transaction = (
                TransferTransaction()
                .addHbarTransfer(AccountId.fromString(self.escrow_account_id), amount.negated())
                .addHbarTransfer(AccountId.fromString(to_account_id), amount)
                .setTransactionMemo(memo)
            )
            
            # Execute transaction
            response = transaction.execute(self.client)
            receipt = response.getReceipt(self.client)
            
            # Get transaction hash
            tx_hash = str(response.transactionId)
            
            print(f"Released {amount} HBAR from escrow to {to_account_id}")
            print(f"Transaction hash: {tx_hash}")
            
            return tx_hash
            
        except Exception as e:
            print(f"Error releasing from escrow: {e}")
            return None
    
    def refund_to_investor(
        self,
        to_account_id: str,
        amount: Decimal,
        memo: str = "Refund"
    ) -> Optional[str]:
        """
        Refund funds from escrow back to investor.
        Called if funding request is cancelled or fails.
        
        Args:
            to_account_id: Hedera account ID of investor
            amount: Amount to refund in HBAR
            memo: Transaction memo
        
        Returns:
            Transaction hash if successful
        """
        return self.release_from_escrow(to_account_id, amount, memo)
    
    def get_escrow_balance(self) -> Optional[Decimal]:
        """
        Get current balance of escrow account.
        Useful for monitoring and auditing.
        """
        if not self.client:
            return Decimal("1000.00")  # Mock balance
        
        try:
            # Query account balance
            from hiero_sdk_python import CryptoGetAccountBalanceQuery
            
            query = CryptoGetAccountBalanceQuery().setAccountId(AccountId.fromString(self.escrow_account_id))
            balance = query.execute(self.client)
            
            # Convert to Decimal
            hbar_balance = balance.hbars
            return Decimal(str(hbar_balance))
            
        except Exception as e:
            print(f"Error querying escrow balance: {e}")
            return None
    
    def _mock_transaction_hash(self) -> str:
        """Generate mock transaction hash for development"""
        timestamp = time.time()
        return f"0.0.{int(timestamp)}@{timestamp:.6f}"


# OFD Integration Stubs (for future)
class OFDService:
    """
    Placeholder for OFD (Oracle Free Dollar) integration.
    
    When OFD is integrated:
    1. Replace HBAR with OFD token transfers
    2. Use OFD token ID from settings
    3. Implement approve/transferFrom pattern
    4. Add OFD-specific transaction logic
    """
    
    def __init__(self):
        self.ofd_enabled = settings.OFD_ENABLED
        self.ofd_token_id = settings.OFD_TOKEN_ID
        self.ofd_contract_address = settings.OFD_CONTRACT_ADDRESS
    
    def ofd_approve_spend(self, spender_address: str, amount: Decimal) -> Optional[str]:
        """
        Approve OFD tokens for spending (ERC20-style approve).
        To be implemented when OFD integration is added.
        """
        raise NotImplementedError("OFD integration pending")
    
    def ofd_deposit(self, from_account: str, amount: Decimal) -> Optional[str]:
        """
        Deposit OFD tokens to escrow contract.
        To be implemented when OFD integration is added.
        """
        raise NotImplementedError("OFD integration pending")
    
    def ofd_release(self, to_account: str, amount: Decimal) -> Optional[str]:
        """
        Release OFD tokens from escrow to recipient.
        To be implemented when OFD integration is added.
        """
        raise NotImplementedError("OFD integration pending")


# Singleton instances
escrow_service = EscrowService()
ofd_service = OFDService()
