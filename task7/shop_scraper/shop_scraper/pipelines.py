# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter
from urllib.parse import urlparse


class ShopScraperPipeline:
    def process_item(self, item, spider):
        return item


class ShopImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for file_url in adapter['photos']:
            if "/width:400/height:400/" in file_url:
                yield scrapy.Request(file_url)

    def file_path(self, request, response=None, info=None, *, item=None):
        title = item.get('title', 'unknown').replace(
            ', ', '_').replace(' ', '_').replace('/', '_')
        filename = os.path.basename(urlparse(request.url).path)
        return f'{title}/{filename}'
