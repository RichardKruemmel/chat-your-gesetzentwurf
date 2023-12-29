import os
import pytest
from unittest.mock import patch
from scrapy.http import Response
from app.scraper.spiders.election_program_spider import ElectionProgramSpider


@pytest.fixture
def spider():
    return ElectionProgramSpider()


@patch("app.scraper.spiders.election_program_spider.load_entity_from_db")
def test_start_requests(mock_load_entity_from_db, spider):
    # Mock data
    mock_programs = [
        MockProgram(
            abgeordnetenwatch_file_url="https://example.com/program1",
            id=1,
            election_id=1,
        ),
        MockProgram(
            abgeordnetenwatch_file_url="https://example.com/program2",
            id=2,
            election_id=1,
        ),
    ]
    mock_load_entity_from_db.return_value = mock_programs

    # Call the function
    requests = list(spider.start_requests())

    # Assertions
    assert len(requests) == 2
    assert requests[0].url == "https://example.com/program1"
    assert requests[0].cb_kwargs == {"program_id": 1, "election_id": 1}
    assert requests[1].url == "https://example.com/program2"
    assert requests[1].cb_kwargs == {"program_id": 2, "election_id": 1}


def test_parse(spider):
    # Mock data
    program_id = 1
    election_id = 1
    response = Response(url="https://example.com/program1", body=b"Program content")

    # Mock the S3Uploader
    spider.s3_uploader = MockS3Uploader()

    # Call the function
    spider.parse(response, program_id, election_id)

    # Assertions
    assert spider.s3_uploader.uploaded_program_id == program_id
    assert spider.s3_uploader.uploaded_election_id == election_id
    assert spider.s3_uploader.uploaded_content == b"Program content"


class MockProgram:
    def __init__(self, abgeordnetenwatch_file_url, id, election_id):
        self.abgeordnetenwatch_file_url = abgeordnetenwatch_file_url
        self.id = id
        self.election_id = election_id


class MockS3Uploader:
    def __init__(self):
        self.uploaded_program_id = None
        self.uploaded_election_id = None
        self.uploaded_content = None

    def upload_to_s3(self, program_id, election_id, content):
        self.uploaded_program_id = program_id
        self.uploaded_election_id = election_id
        self.uploaded_content = content
