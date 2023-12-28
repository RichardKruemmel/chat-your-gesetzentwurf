from app.database import models


def assert_file_cloud_urls_updated(test_session, test_s3_bucket_name):
    election_programs = test_session.query(models.ElectionProgram).all()
    test_s3_bucket_url = f"https://{test_s3_bucket_name}.s3.eu-central-1.amazonaws.com"
    for program in election_programs:
        expected_url = f"{test_s3_bucket_url}/{program.election_id}/{program.id}.pdf"
        assert (
            program.file_cloud_url == expected_url
        ), "File cloud URL not updated correctly."
