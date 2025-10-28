import os
import json
from hedera import (
    Client,
    TopicCreateTransaction,
    TopicMessageSubmitTransaction,
)

OPERATOR_ID = os.environ.get("OPERATOR_ID")
OPERATOR_KEY = os.environ.get("OPERATOR_KEY")

client = Client.forTestnet()
client.setOperator(OPERATOR_ID, OPERATOR_KEY)

def create_topic():
    """Creates a new HCS topic."""
    # transaction = TopicCreateTransaction().execute(client)
    # receipt = transaction.getReceipt(client)
    # return receipt.topicId
    print("Creating HCS topic")
    return "mock-topic-id"

def submit_message(topic_id, message):
    """Submits a message to an HCS topic."""
    # transaction = TopicMessageSubmitTransaction(
    #     topicId=topic_id,
    #     message=json.dumps(message),
    # ).execute(client)
    # receipt = transaction.getReceipt(client)
    # return receipt.status
    print(f"Submitting message to HCS topic {topic_id}: {json.dumps(message)}")
    return "SUCCESS"
