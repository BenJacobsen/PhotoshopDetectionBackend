import boto3
from botocore.config import Config
s3 = boto3.resource(
    service_name='s3',
    region_name=,
    aws_access_key_id=,
    aws_secret_access_key= 
)
for bucket in s3.buckets.all():
    print(bucket.name)

s3.Bucket().upload_file(Filename=, Key='test2.txt')