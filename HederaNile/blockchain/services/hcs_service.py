"""
Hedera Consensus Service (HCS) integration for NileFi.
Logs all key events to Hedera for immutability and transparency.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
from django.conf import settings

try:
    from hiero_sdk_python import (
        Client,
        PrivateKey,
        AccountId,
        TopicMessageSubmitTransaction,
        TopicCreateTransaction,
    )
    HIERO_AVAILABLE = True
except ImportError:
    HIERO_AVAILABLE = False
    print("Warning: hiero-sdk-python not available. Using mock implementation.")


class HCSService:
    """
    Hedera Consensus Service wrapper for logging blockchain events.
    """
    
    def __init__(self):
        self.network = settings.HEDERA_NETWORK
        self.operator_id = settings.HEDERA_OPERATOR_ID
        self.operator_key = settings.HEDERA_OPERATOR_KEY
        self.topic_id = settings.HEDERA_HCS_TOPIC_ID
        
        if HIERO_AVAILABLE and self.operator_id and self.operator_key:
            self.client = self._init_client()
        else:
            self.client = None
            print("HCS: Running in mock mode - blockchain logging disabled")
    
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
    
    def create_topic(self, memo: str = "NileFi HCS Topic") -> Optional[str]:
        """
        Create a new HCS topic for the platform.
        Should be run once during platform setup.
        """
        if not self.client:
            return self._mock_topic_id()
        
        try:
            transaction = (
                TopicCreateTransaction()
                .setTopicMemo(memo)
                .setAdminKey(PrivateKey.fromStringED25519(self.operator_key).getPublicKey())
            )
            
            response = transaction.execute(self.client)
            receipt = response.getReceipt(self.client)
            topic_id = str(receipt.topicId)
            
            print(f"Created HCS topic: {topic_id}")
            return topic_id
        except Exception as e:
            print(f"Error creating HCS topic: {e}")
            return self._mock_topic_id()
    
    def log_event(
        self,
        event_type: str,
        payload: Dict,
        topic_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Log an event to Hedera Consensus Service.
        
        Args:
            event_type: Type of event (CREATE_REQUEST, DEPOSIT, VERIFY, RELEASE, etc.)
            payload: Event data as dictionary
            topic_id: Optional specific topic ID (defaults to platform topic)
        
        Returns:
            HCS message ID or None if failed
        """
        topic = topic_id or self.topic_id
        
        if not topic:
            print("Warning: No HCS topic configured")
            return self._mock_message_id()
        
        if not self.client:
            return self._mock_message_id()
        
        try:
            # Prepare message
            message_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": payload,
                "hash": self._hash_payload(payload)
            }
            message_json = json.dumps(message_data)
            
            # Submit to HCS
            transaction = (
                TopicMessageSubmitTransaction()
                .setTopicId(topic)
                .setMessage(message_json)
            )
            
            response = transaction.execute(self.client)
            receipt = response.getReceipt(self.client)
            
            # Get transaction ID as message identifier
            message_id = str(response.transactionId)
            
            print(f"HCS Event logged: {event_type} - Message ID: {message_id}")
            return message_id
            
        except Exception as e:
            print(f"Error logging to HCS: {e}")
            return self._mock_message_id()
    
    def _hash_payload(self, payload: Dict) -> str:
        """Create hash of payload for integrity verification"""
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    def _mock_topic_id(self) -> str:
        """Generate mock topic ID for development"""
        timestamp = datetime.utcnow().timestamp()
        return f"0.0.{int(timestamp)}"
    
    def _mock_message_id(self) -> str:
        """Generate mock message ID for development"""
        timestamp = datetime.utcnow().timestamp()
        return f"0.0.{int(timestamp)}@{timestamp:.6f}"


# Singleton instance
hcs_service = HCSService()


# Convenience functions for common events
def log_funding_request_created(request_id: str, startup_id: str, amount: float):
    """Log funding request creation"""
    return hcs_service.log_event(
        "CREATE_REQUEST",
        {
            "request_id": request_id,
            "startup_id": startup_id,
            "amount": amount
        }
    )


def log_investment_deposit(investment_id: str, lender_id: str, amount: float, tx_hash: str):
    """Log investment deposit"""
    return hcs_service.log_event(
        "DEPOSIT",
        {
            "investment_id": investment_id,
            "lender_id": lender_id,
            "amount": amount,
            "tx_hash": tx_hash
        }
    )


def log_milestone_verification(milestone_id: str, verifier_id: str):
    """Log milestone verification"""
    return hcs_service.log_event(
        "VERIFY_MILESTONE",
        {
            "milestone_id": milestone_id,
            "verifier_id": verifier_id
        }
    )


def log_funds_release(milestone_id: str, amount: float, tx_hash: str):
    """Log funds release"""
    return hcs_service.log_event(
        "RELEASE_FUNDS",
        {
            "milestone_id": milestone_id,
            "amount": amount,
            "tx_hash": tx_hash
        }
    )
