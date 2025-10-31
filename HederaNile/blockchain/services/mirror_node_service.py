"""
Hedera Mirror Node API integration for NileFi.
Queries transaction history and status from Mirror Node REST API.
"""

import requests
from typing import Dict, Optional, List
from django.conf import settings


class MirrorNodeService:
    """
    Hedera Mirror Node REST API wrapper.
    Used to query transaction details, account history, and HCS messages.
    """
    
    def __init__(self):
        self.base_url = settings.HEDERA_MIRROR_NODE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """
        Get transaction details by transaction ID.
        
        Args:
            transaction_id: Hedera transaction ID (format: 0.0.XXXX@timestamp.nanoseconds)
        
        Returns:
            Transaction details dict or None if not found
        """
        try:
            url = f"{self.base_url}/api/v1/transactions/{transaction_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('transactions'):
                    return data['transactions'][0]
            
            return None
            
        except Exception as e:
            print(f"Error fetching transaction {transaction_id}: {e}")
            return None
    
    def get_account_transactions(
        self,
        account_id: str,
        limit: int = 10,
        transaction_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get transaction history for an account.
        
        Args:
            account_id: Hedera account ID (0.0.XXXX)
            limit: Number of transactions to return
            transaction_type: Optional filter (CRYPTOTRANSFER, TOKENTRANSFER, etc.)
        
        Returns:
            List of transaction dicts
        """
        try:
            url = f"{self.base_url}/api/v1/transactions"
            params = {
                'account.id': account_id,
                'limit': limit,
                'order': 'desc'
            }
            
            if transaction_type:
                params['transactionType'] = transaction_type
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('transactions', [])
            
            return []
            
        except Exception as e:
            print(f"Error fetching account transactions for {account_id}: {e}")
            return []
    
    def get_hcs_messages(
        self,
        topic_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get HCS messages from a topic.
        
        Args:
            topic_id: HCS topic ID (0.0.XXXX)
            limit: Number of messages to return
        
        Returns:
            List of HCS message dicts
        """
        try:
            url = f"{self.base_url}/api/v1/topics/{topic_id}/messages"
            params = {
                'limit': limit,
                'order': 'desc'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('messages', [])
            
            return []
            
        except Exception as e:
            print(f"Error fetching HCS messages for topic {topic_id}: {e}")
            return []
    
    def get_transaction_status(self, transaction_id: str) -> Optional[str]:
        """
        Get transaction status (SUCCESS, FAILED, etc.).
        
        Args:
            transaction_id: Hedera transaction ID
        
        Returns:
            Status string or None
        """
        tx = self.get_transaction(transaction_id)
        if tx:
            return tx.get('result', 'UNKNOWN')
        return None
    
    def verify_transfer(
        self,
        transaction_id: str,
        expected_from: str,
        expected_to: str,
        expected_amount: Optional[float] = None
    ) -> bool:
        """
        Verify a transfer transaction matches expected parameters.
        
        Args:
            transaction_id: Transaction ID to verify
            expected_from: Expected sender account ID
            expected_to: Expected recipient account ID
            expected_amount: Optional expected amount in tinybars
        
        Returns:
            True if transaction matches expectations
        """
        try:
            tx = self.get_transaction(transaction_id)
            if not tx:
                return False
            
            # Check transaction succeeded
            if tx.get('result') != 'SUCCESS':
                return False
            
            # Check transfers
            transfers = tx.get('transfers', [])
            from_found = False
            to_found = False
            
            for transfer in transfers:
                account = transfer.get('account')
                amount = transfer.get('amount', 0)
                
                if account == expected_from and amount < 0:
                    from_found = True
                    if expected_amount and abs(amount) != expected_amount:
                        return False
                
                if account == expected_to and amount > 0:
                    to_found = True
                    if expected_amount and amount != expected_amount:
                        return False
            
            return from_found and to_found
            
        except Exception as e:
            print(f"Error verifying transfer: {e}")
            return False
    
    def get_account_balance(self, account_id: str) -> Optional[float]:
        """
        Get current account balance in HBAR.
        
        Args:
            account_id: Hedera account ID
        
        Returns:
            Balance in HBAR or None
        """
        try:
            url = f"{self.base_url}/api/v1/balances"
            params = {
                'account.id': account_id
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                balances = data.get('balances', [])
                if balances:
                    # Convert from tinybars to HBAR
                    balance_tinybars = balances[0].get('balance', 0)
                    return balance_tinybars / 100_000_000
            
            return None
            
        except Exception as e:
            print(f"Error fetching account balance for {account_id}: {e}")
            return None


# Singleton instance
mirror_node_service = MirrorNodeService()
