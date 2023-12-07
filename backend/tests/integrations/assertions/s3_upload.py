import boto3
from botocore.exceptions import ClientError

from app.database import models


def assert_correct_s3_upload(session, access_key, secret_key, s3_bucket_name):
    election_programs = session.query(models.ElectionProgram).all()
    s3_client = boto3.client(
        "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
    )

    for program in election_programs:
        object_key = f"{program.election_id}/{program.id}.pdf"
        try:
            # Check if the object exists in the bucket
            s3_client.head_object(Bucket=s3_bucket_name, Key=object_key)
            print(f"Verified: File {object_key} exists in S3 bucket.")
        except ClientError as e:
            # If the object does not exist, an exception is thrown
            assert False, f"File {object_key} does not exist in S3 bucket."
