import os
import scrapy

from app.scraper.utils.s3_uploader import S3Uploader
import app.database.models as models
from app.database.utils.db_utils import load_entity_from_db

class ElectionProgramSpider(scrapy.Spider):
    name = "electionprogramspider"

    def __init__(self, *args, **kwargs):
        super(ElectionProgramSpider, self).__init__(*args, **kwargs)
        s3_access_key = os.environ.get("S3_ACCESS_KEY")
        s3_secret = os.environ.get("S3_SECRET")
        self.s3_uploader = S3Uploader(s3_access_key, s3_secret)

    def start_requests(self):
        election_programs = load_entity_from_db(models.ElectionProgram)
        for program in election_programs:
            yield scrapy.Request(
                url=program.abgeordnetenwatch_file_url,
                cb_kwargs={
                    "program_id": program.id,
                    "election_id": program.election_id,
                },
            )

    def parse(self, response, program_id, election_id):
        self.s3_uploader.upload_to_s3(program_id, election_id, response.body)
