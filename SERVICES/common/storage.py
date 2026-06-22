import os
from datetime import datetime, timezone
from typing import Dict


def store_resume_object(filename: str, content: bytes) -> Dict[str, str]:
    bucket = os.getenv("S3_BUCKET", "local-resume-bucket")
    local_dir = os.getenv("LOCAL_OBJECT_STORE", "object-store")
    safe_filename = os.path.basename(filename)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    object_key = f"resumes/{timestamp}-{safe_filename}"

    if os.getenv("AWS_EXECUTION_ENV"):
        import boto3

        client = boto3.client("s3")
        client.put_object(Bucket=bucket, Key=object_key, Body=content)
    else:
        path = os.path.join(local_dir, object_key.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as output:
            output.write(content)

    return {
        "bucket": bucket,
        "object_key": object_key,
        "uri": f"s3://{bucket}/{object_key}",
    }
