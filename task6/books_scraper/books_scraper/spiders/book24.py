import scrapy
from books_scraper.items import BooksScraperItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/catalog/']

    def parse(self, response):
        cards = response.css('div.product-list__item')
        if not cards:
            print('Cards not found')
            return

        for card in cards:
            url_book = card.css('a.product-card__image-link::attr(href)').get()
            if not url_book:
                print('URL book not found')
                continue

            yield response.follow(url_book, callback=self.parse_book_info)

        next_page = response.css('li.pagination__button-item._next a::attr(href)').get()
        if next_page:
           yield response.follow(next_page, callback=self.parse)

    def parse_book_info(self, response):
        item = BooksScraperItem()
        item['url'] = response.url
        full_title = response.css('h1.product-detail-page__title::text').get()
        item['title'] = self.parse_title(full_title)

        item['authors'] = response.css(
            'dd.product-characteristic__value a[href^="/author/"]::text').getall()

        discounted_price = response.css(
            'span.app-price.product-sidebar-price__price meta[itemprop="price"]::attr(content)').get()
        item['discounted_price'] = self.format_price(discounted_price)

        base_price = response.css(
            'span.app-price.product-sidebar-price__price-old::text').get()

        item['base_price'] = self.format_price(base_price)

        item['sections'] = response.css(
            'dd.product-characteristic__value a[href^="/catalog/"]::text').getall()
        
        print(item)
        yield item

    def parse_title(self, title):
        if not title:
            return None

        full_title = title.strip()

        if ':' in full_title:
            return full_title.split(':', 1)[1].strip()

        return full_title

    def format_price(self, price):
        if not price:
            return None

        price = price.replace(
            '\xa0', '').replace('&nbsp;', '').replace('₽', '').strip()

        return int(price)
