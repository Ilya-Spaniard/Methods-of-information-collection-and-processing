import scrapy
from selenium import webdriver
from scrapy.http import TextResponse
from scrapy.loader import ItemLoader
from shop_scraper.items import ShopScraperItem


class CitilinkSpider(scrapy.Spider):
    name = 'citilink'
    allowed_domains = ['citilink.ru']

    driver = webdriver.Chrome()

    start_urls = [
        'https://www.citilink.ru/catalog/wi-fi-routery-marshrutizatory/']

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.implicitly_wait(10)
        selenium_response = TextResponse(url=response.url,
                                         body=self.driver.page_source,
                                         encoding='utf-8')

        return self.parse_catalog_page(selenium_response)

    def parse_catalog_page(self, response):
        products = response.css('div[data-meta-name="ProductListLayout"]')
        cards = products.css(
            'div[data-meta-name="SnippetProductVerticalLayout"]')
        if not cards:
            print('Cards not found')
            return

        for card in cards:
            url_product = card.css('a[href^="/product/"]::attr(href)').get()
            if not url_product:
                print('URL product not found')
                continue
            yield response.follow(url_product, callback=self.parse_product_page)

    def parse_product_page(self, response):
        loader = ItemLoader(item=ShopScraperItem(), response=response)
        loader.add_css('title', 'h1::text')
        loader.add_value('url', response.url)
        loader.add_css(
            'price', 'div.app-catalog-iqmcm0-StyledPriceAndButtonWrapper.e1su85tu0 [data-meta-price]::attr(data-meta-price)')
        loader.add_css(
            'photos', 'div.app-catalog-hugbyn-Flex--StyledFlex-Container--StyledContainer img::attr(src)')

        yield loader.load_item()
