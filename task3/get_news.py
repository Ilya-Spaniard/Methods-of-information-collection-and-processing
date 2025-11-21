import sys
import requests
from lxml import html
from pymongo import MongoClient


def get_news(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f'Error executing request to {url}: {response.status_code}')
        sys.exit(1)

    return response.text


def parse_news_lenta():
    news_list = []
    url_lenta = 'https://lenta.ru/parts/news/'
    page = get_news(url_lenta)
    tree = html.fromstring(page)
    news = tree.xpath("//li[@class='parts-page__item']")

    for new in news:
        url = new.xpath(
            ".//a[@class='card-full-news _parts-news']/@href")[0].strip()
        title = new.xpath(
            ".//h3[@class='card-full-news__title']/text()")[0].strip()
        time = new.xpath(
            ".//time[@class='card-full-news__info-item card-full-news__date']/text()")[0].strip()

        news_list.append({
            'Source': 'lenta.ru',
            'Title': title,
            'URL': 'https://lenta.ru' + url,
            'Time': time
        })

    return news_list


def get_collection_mongodb(database_name: str, collection_name: str):
    client = MongoClient('')
    db = client[database_name]
    collection = db[collection_name]
    return collection


def save_news_to_mongodb(news_list: list):
    collection = get_collection_mongodb('my_database', 'news')

    for new in news_list:
        result = collection.update_one(
            {'URL': new['URL'], 'Title': new['Title']},
            {'$set': new},
            upsert=True
        )
    print(result)


def main():
    news_list = parse_news_lenta()
    save_news_to_mongodb(news_list)


if __name__ == '__main__':
    main()
