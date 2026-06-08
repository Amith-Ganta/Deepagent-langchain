# AWS Skill — Canonical Example

One complete, production-ready example showing boto3 best practices.

---

## Serverless File Processor: S3 → Lambda → DynamoDB

**Scenario:** A Lambda function triggered by an S3 upload that parses a JSON file and stores records in DynamoDB. Demonstrates IAM, error handling, paginators, and logging.

### IAM Policy (least-privilege)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadSourceBucket",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-input-bucket/*"
    },
    {
      "Sid": "WriteRecordsTable",
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem", "dynamodb:BatchWriteItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/Records"
    },
    {
      "Sid": "Logs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/file-processor:*"
    }
  ]
}
```

### Lambda Handler
```python
import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ["RECORDS_TABLE"]   # injected via Lambda env var

s3 = boto3.client("s3", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event: dict, context) -> dict:
    """Process an S3 PutObject event, store records in DynamoDB.

    Expected event: S3 trigger (EventBridge or direct S3 notification).
    """
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        logger.info("Processing s3://%s/%s", bucket, key)

        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
        except ClientError as e:
            logger.error("S3 get failed: %s", e.response["Error"]["Code"])
            raise

        data = json.loads(obj["Body"].read())
        _batch_write(data.get("records", []))
        logger.info("Stored %d records from %s", len(data.get("records", [])), key)

    return {"statusCode": 200}


def _batch_write(records: list[dict]) -> None:
    """Write records to DynamoDB in batches of 25."""
    with table.batch_writer() as batch:
        for item in records:
            batch.put_item(Item=item)
```

### Deployment (AWS CLI)
```bash
# Package
zip function.zip lambda_handler.py

# Create / update
aws lambda create-function \
  --function-name file-processor \
  --runtime python3.12 \
  --handler lambda_handler.lambda_handler \
  --role arn:aws:iam::123456789012:role/LambdaFileProcessorRole \
  --zip-file fileb://function.zip \
  --environment Variables={RECORDS_TABLE=Records} \
  --region us-east-1
```

**How it works:**
- IAM policy grants only what the function needs — no wildcards.
- `boto3.resource` (higher-level) for DynamoDB; `boto3.client` (lower-level) for S3.
- `ClientError` is caught explicitly with the error code logged for diagnostics.
- `batch_writer()` auto-batches up to 25 items per `BatchWriteItem` call.
- `TABLE_NAME` comes from an env var — never hardcoded.
- **Cost**: Lambda + S3 + DynamoDB on-demand = pay-per-invocation; ~$0 at low volume.
