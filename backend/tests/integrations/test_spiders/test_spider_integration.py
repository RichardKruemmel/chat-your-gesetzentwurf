import os
from unittest.mock import MagicMock, patch
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from app.scraper.spiders.election_program_spider import ElectionProgramSpider
from app.scraper.utils.s3_uploader import S3Uploader

from tests.integrations.assertions.s3_upload import assert_correct_s3_upload
from tests.integrations.assertions.data_extraction import assert_correct_data_extraction
from tests.integrations.setup.setup_test_db import setup_test_database
from tests.integrations.setup.setup_test_server import setup_test_server


def test_spider_integration():
    # Setup test server and database
    httpd = setup_test_server()
    engine, test_session = setup_test_database()

    # Define S3 test bucket and credentials
    S3_TEST_BUCKET = "test-election-program"
    S3_TEST_ACCESS_KEY = os.getenv("S3_TEST_ACCESS_KEY")
    S3_TEST_SECRET_KEY = os.getenv("S3_TEST_SECRET_KEY")
    TEST_DATA_DIRECTORY = "tests/integrations/test_data/test_programs/"

    # Run the spider
    settings = get_project_settings()
    settings.set("SQLALCHEMY_DATABASE_URI", engine.url)
    settings.set("BASE_API_URL", "http://localhost:8000")

    process = CrawlerProcess(settings)
    process.crawl(
        ElectionProgramSpider,
        s3_access_key=S3_TEST_ACCESS_KEY,
        s3_secret=S3_TEST_SECRET_KEY,
        s3_bucket_name=S3_TEST_BUCKET,
    )
    process.start()

    # Validate S3 interactions
    assert_correct_s3_upload(
        test_session, S3_TEST_ACCESS_KEY, S3_TEST_SECRET_KEY, S3_TEST_BUCKET
    )

    # Validate extraction
    assert_correct_data_extraction(
        test_session,
        S3_TEST_BUCKET,
        S3_TEST_ACCESS_KEY,
        S3_TEST_SECRET_KEY,
        TEST_DATA_DIRECTORY,
    )

    """# Validate database interactions
        assert_correct_database_interaction()

        # Validate S3 interactions
        assert_correct_s3_interaction()
    """
    # Clean up
    httpd.shutdown()
    test_session.close()
