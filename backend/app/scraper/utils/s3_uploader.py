import boto3
import botocore
import logging


class S3Uploader:
    def __init__(self, access_key, secret_key):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def upload_to_s3(self, program_id, election_id, file_data):
        try:
            self.s3_client.put_object(
                Bucket="election-program",
                Key=f"{election_id}/{program_id}.pdf",
                Body=file_data,
                ACL="public-read",
                ContentType="application/pdf",
            )
            logging.info(f"Successfully uploaded election program {program_id} to S3.")
        except botocore.exceptions.ClientError as e:
            logging.error(
                f"Client error uploading election program {program_id} to S3: {str(e)}"
            )
        except botocore.exceptions.NoCredentialsError as e:
            logging.error(
                f"No credentials error uploading election program {program_id} to S3: {str(e)}"
            )
        except Exception as e:
            logging.error(
                f"Error uploading election program {program_id} to S3: {str(e)}"
            )
