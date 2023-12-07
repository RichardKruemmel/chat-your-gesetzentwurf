import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from app.scraper.scripts.update_db import update_db
from app.scraper.spiders.election_program_spider import ElectionProgramSpider

from tests.integrations.assertions.database_updates import (
    assert_correct_database_updates,
)
from tests.integrations.assertions.s3_upload import assert_correct_s3_upload
from tests.integrations.assertions.data_extraction import assert_correct_data_extraction
from tests.integrations.setup.setup_test_db import setup_test_database
from tests.integrations.setup.setup_test_server import setup_test_server
from tests.integrations.setup.teardown_s3 import teardown_s3


def test_integration():
    # Setup test server mimicking the AbgeordnetenWatch API
    httpd = setup_test_server()

    # Setup test database with initial data
    engine, test_session = setup_test_database()

    # Define S3 test bucket
    S3_TEST_BUCKET = "test-election-program"
    S3_TEST_ACCESS_KEY = os.getenv("S3_TEST_ACCESS_KEY")
    S3_TEST_SECRET_KEY = os.getenv("S3_TEST_SECRET_KEY")
    TEST_DATA_DIRECTORY = "tests/integrations/test_data"

    # Set BASE_API_URL to local server for both tests
    settings = get_project_settings()
    settings.set("BASE_API_URL", "http://localhost:8000")
    os.environ["BASE_URL"] = "http://localhost:8000"

    # Run the update_db function
    update_db(test_session)

    # Assert database updates
    assert_correct_database_updates(test_session)

    # Setup the spider for test_spider_integration
    process = CrawlerProcess(settings)
    process.crawl(
        ElectionProgramSpider,
        s3_access_key=S3_TEST_ACCESS_KEY,
        s3_secret=S3_TEST_SECRET_KEY,
        s3_bucket_name=S3_TEST_BUCKET,
    )
    process.start()

    # Validate extraction and S3 interactions
    assert_correct_data_extraction(
        test_session,
        S3_TEST_BUCKET,
        S3_TEST_ACCESS_KEY,
        S3_TEST_SECRET_KEY,
        TEST_DATA_DIRECTORY,
    )
    assert_correct_s3_upload(
        test_session, S3_TEST_ACCESS_KEY, S3_TEST_SECRET_KEY, S3_TEST_BUCKET
    )

    # Teardown S3 bucket
    teardown_s3(S3_TEST_BUCKET, S3_TEST_ACCESS_KEY, S3_TEST_SECRET_KEY, test_session)

    # Clean up: remove environment variable, shutdown server, and close session
    del os.environ["BASE_URL"]
    httpd.shutdown()
    test_session.close()
