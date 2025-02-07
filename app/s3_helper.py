from functools import lru_cache

import boto3
import os
from botocore.exceptions import ClientError
from uuid import uuid4


@lru_cache(maxsize=None)
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )


def upload_file_to_s3(file, bucket_name=None):
    s3 = get_s3_client()
    bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME')

    try:
        filename = f"comments/{uuid4().hex}"
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        return filename
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None


def generate_s3_url(filename, bucket_name=None, expiration=3600):
    s3 = get_s3_client()
    bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME')

    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"Error generating URL: {e}")
        return None