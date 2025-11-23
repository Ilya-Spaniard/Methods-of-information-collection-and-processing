# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def parse_price(price):
    if not price:
        return None

    price = price.replace(
        '\xa0', '').replace('&nbsp;', '').replace(' ', '').strip()

    return int(price)


class ShopScraperItem(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(
        parse_price), output_processor=TakeFirst())
