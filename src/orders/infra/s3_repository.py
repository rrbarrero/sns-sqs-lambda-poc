from domain.order import Order


class S3Repository:
    def __init__(self, client):
        self.client = client

    def upload_file(self, bucket_name, file_name, order: Order):
        try:
            self.client.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=order.to_json_string(),
            )
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
        return True
