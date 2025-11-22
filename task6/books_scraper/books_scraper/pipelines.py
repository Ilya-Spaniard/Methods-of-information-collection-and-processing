# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class BooksScraperPipeline:
    def process_item(self, item, spider):
        return item


class MongoPipeline:
    COLLECTION_NAME = "books"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get("url")

        if self.db[self.COLLECTION_NAME].find_one({"url": url}):
            raise DropItem(f"Duplicate item found: {url}")
        else:
            self.db[self.COLLECTION_NAME].insert_one(adapter.asdict())
            return item
