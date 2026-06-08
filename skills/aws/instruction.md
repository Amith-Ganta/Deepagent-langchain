# AWS Skill — Quick-Start Reference

A one-page cheat sheet for the deep agent. Read `instructions.md` for the full workflow.

## Service Selection Shortcuts
| Need | First choice | When to escalate |
|------|-------------|-----------------|
| Run code | Lambda | >15 min or needs GPU → Fargate/EC2 |
| Store objects | S3 | Block-level → EBS; shared POSIX → EFS |
| Key-value DB | DynamoDB | Relational/SQL → RDS Aurora |
| Queue | SQS | Pub/sub fanout → SNS; event routing → EventBridge |
| REST API | API Gateway + Lambda | Sustained traffic → ALB + ECS |
| GenAI models | Bedrock (Claude) | Custom training → SageMaker |

## Non-Negotiable Security Rules
1. **Least-privilege IAM** — narrow `Action` and `Resource`; never `"*"` on both.
2. **No hard-coded credentials** — IAM roles on AWS, `~/.aws/profiles` locally.
3. **Encrypt at rest** — enable SSE on S3, encryption on RDS/EBS by default.
4. **Block Public Access** on all S3 buckets unless serving public static content.
5. **Secrets** → AWS Secrets Manager or SSM Parameter Store, never in code/git.

## Minimal boto3 Pattern
```python
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3", region_name="us-east-1")   # explicit region always

try:
    s3.upload_file("local.txt", "my-bucket", "data/local.txt")
except ClientError as e:
    print(e.response["Error"]["Code"])   # e.g. "AccessDenied", "NoSuchBucket"
```

## CLI Essentials
```bash
aws sts get-caller-identity              # who am I?
aws s3 ls s3://my-bucket --recursive     # list all objects
aws logs tail /aws/lambda/my-fn --follow # live Lambda logs
aws bedrock-runtime converse ...         # call a foundation model
```

## AccessDenied Checklist
1. `aws sts get-caller-identity` — confirm the actual identity
2. IAM policy — does it allow the exact action + ARN?
3. Resource policy (bucket/key policy) — any explicit deny?
4. SCP / permission boundary — org-level overrides?
5. KMS — does the role also have `kms:Decrypt`?
