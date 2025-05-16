from domain.order import Order


class SNSRepository:
    def __init__(self, sns_client):
        self.sns_client = sns_client

    def publish_message(self, topic_arn, order: Order):
        response = self.sns_client.publish(
            TopicArn=topic_arn, Message=order.to_json_string()
        )
        return response


class InMemorySNSRepository:
    def __init__(self):
        self.published_messages = []

    def publish_message(self, topic_arn, order: Order):
        self.published_messages.append(order.to_json_string())
        return {"MessageId": str(len(self.published_messages) - 1)}
