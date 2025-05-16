class SQSRepository:
    def __init__(self, client):
        self.client = client

    def receive_message(self, queue_url):
        response = self.client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )
        return response.get("Messages", [])

    def delete_message(self, queue_url, receipt_handle):
        self.client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )
        return True
