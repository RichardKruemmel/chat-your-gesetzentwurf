import boto3
from botocore.exceptions import ClientError

from app.database import models


def teardown_s3(bucket_name, access_key, secret_key, session):
    s3_client = boto3.client(
        "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
    )

    for program in session.query(models.ElectionProgram).all():
        object_key = f"{program.election_id}/{program.id}.pdf"

        try:
            s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            print(f"Deleted file {object_key} from S3 bucket {bucket_name}.")
        except ClientError as e:
            print(f"Failed to delete {object_key} from S3 bucket {bucket_name}: {e}")

    print("S3 bucket cleanup complete.")
