import os
import boto3

from app.database import models


def assert_correct_data_extraction(
    session, s3_bucket_name, s3_access_key, s3_secret_key, test_data_directory
):
    s3_client = boto3.client(
        "s3", aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key
    )

    for program in session.query(models.ElectionProgram).all():
        object_key = f"{program.election_id}/{program.id}.pdf"
        expected_file_path = os.path.join(
            test_data_directory, f"program_{program.id}.json"
        )

        # Download the file from S3
        s3_file = s3_client.get_object(Bucket=s3_bucket_name, Key=object_key)
        s3_file_content = s3_file["Body"].read()

        # Read the expected content from local file
        with open(expected_file_path, "rb") as f:
            expected_content = f.read()

        # Assert that the contents match
        assert s3_file_content == expected_content, f"Content mismatch for {object_key}"
