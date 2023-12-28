import pytest
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from unittest.mock import patch
from app.scraper.utils.s3_uploader import S3Uploader

# Constants
ACCESS_KEY = "ACCESS_KEY"
SECRET_KEY = "SECRET_KEY"
PROGRAM_ID = "program_id"
ELECTION_ID = "election_id"
FILE_DATA = b"file_data"


# Test for successful upload
@patch("app.scraper.utils.s3_uploader.boto3.client")
@patch("app.scraper.utils.s3_uploader.logging.info")
def test_upload_to_s3_success(mock_logging_info, mock_client):
    mock_s3_client = mock_client.return_value
    mock_s3_client.put_object.return_value = None

    s3_uploader = S3Uploader(ACCESS_KEY, SECRET_KEY, "election-program")
    s3_uploader.upload_to_s3(PROGRAM_ID, ELECTION_ID, FILE_DATA)

    mock_client.assert_called_once_with(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="election-program",
        Key=f"{ELECTION_ID}/{PROGRAM_ID}.pdf",
        Body=FILE_DATA,
        ACL="public-read",
        ContentType="application/pdf",
    )
    mock_logging_info.assert_called_once_with(
        f"Successfully uploaded election program {PROGRAM_ID} to S3."
    )


# Test for handling ClientError
@patch("app.scraper.utils.s3_uploader.boto3.client")
@patch("app.scraper.utils.s3_uploader.logging.error")
def test_upload_to_s3_client_error(mock_logging_error, mock_client):
    mock_s3_client = mock_client.return_value
    mock_s3_client.put_object.side_effect = ClientError(
        {"Error": {"Code": "TestException", "Message": "Test Exception"}}, "PutObject"
    )

    s3_uploader = S3Uploader(ACCESS_KEY, SECRET_KEY, "election-program")
    s3_uploader.upload_to_s3(PROGRAM_ID, ELECTION_ID, FILE_DATA)

    mock_client.assert_called_once_with(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="election-program",
        Key=f"{ELECTION_ID}/{PROGRAM_ID}.pdf",
        Body=FILE_DATA,
        ACL="public-read",
        ContentType="application/pdf",
    )
    mock_logging_error.assert_called()


# Test for handling NoCredentialsError
@patch("app.scraper.utils.s3_uploader.boto3.client")
@patch("app.scraper.utils.s3_uploader.logging.error")
def test_upload_to_s3_no_credentials_error(mock_logging_error, mock_client):
    mock_s3_client = mock_client.return_value
    mock_s3_client.put_object.side_effect = NoCredentialsError()

    s3_uploader = S3Uploader(ACCESS_KEY, SECRET_KEY, "election-program")
    s3_uploader.upload_to_s3(PROGRAM_ID, ELECTION_ID, FILE_DATA)

    mock_client.assert_called_once_with(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="election-program",
        Key=f"{ELECTION_ID}/{PROGRAM_ID}.pdf",
        Body=FILE_DATA,
        ACL="public-read",
        ContentType="application/pdf",
    )
    mock_logging_error.assert_called_once()


# Test for handling generic errors
@patch("app.scraper.utils.s3_uploader.boto3.client")
@patch("app.scraper.utils.s3_uploader.logging.error")
def test_upload_to_s3_generic_error(mock_logging_error, mock_client):
    mock_s3_client = mock_client.return_value
    mock_s3_client.put_object.side_effect = Exception("Generic error")

    s3_uploader = S3Uploader(ACCESS_KEY, SECRET_KEY, "election-program")
    s3_uploader.upload_to_s3(PROGRAM_ID, ELECTION_ID, FILE_DATA)

    mock_client.assert_called_once_with(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="election-program",
        Key=f"{ELECTION_ID}/{PROGRAM_ID}.pdf",
        Body=FILE_DATA,
        ACL="public-read",
        ContentType="application/pdf",
    )
    mock_logging_error.assert_called_once()
