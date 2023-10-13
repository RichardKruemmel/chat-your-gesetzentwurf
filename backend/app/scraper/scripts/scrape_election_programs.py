from scrapy.crawler import CrawlerProcess
from app.scraper.spiders.election_program_spider import ElectionProgramSpider


def scrape_election_programs():
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0",
            "DOWNLOAD_DELAY": 0.5,
            "AUTOTHROTTLE_ENABLED": True,
            "AUTOTHROTTLE_START_DELAY": 0.5,
            "AUTOTHROTTLE_MAX_DELAY": 15,
            "AUTOTHROTTLE_TARGET_CONCURRENCY": 2.0,
        }
    )
    process.crawl(ElectionProgramSpider)
    process.start()

if __name__ == "__main__":
    scrape_election_programs()
