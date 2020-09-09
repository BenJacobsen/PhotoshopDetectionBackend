import boto3
from botocore.config import Config
s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-2',
    aws_access_key_id='AKIA23SDNIJWNVLLAEES',
    aws_secret_access_key= "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"
)
for bucket in s3.buckets.all():
    print(bucket.name)

s3.Bucket('psdetect-bucket').upload_file(Filename='C:\\Github\\test.txt', Key='test2.txt')