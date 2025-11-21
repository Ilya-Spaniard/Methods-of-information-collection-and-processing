import sys
import requests
import pandas as pd
from lxml import html
from pymongo import MongoClient


def check_args(args: list):
    if len(args) != 2:
        print('Incorrect number of arguments')
        sys.exit(1)

    position = args[0]
    pages_quantity = args[1]

    if not pages_quantity.isdigit():
        print('Second argument is not a number')
        sys.exit(1)

    return position, pages_quantity


def get_vacancies_hh(position: str, page_num: int):
    url = 'https://hh.ru/search/vacancy'

    params = {
        'text': position,
        'page': page_num
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print(f'Error executing request to {url}: {response.status_code}')
        sys.exit(1)

    return response.text


def clean_list(lst: list):
    lst_cleaned = []
    for element in lst:
        element_cleaned = element.replace(
            '\u202f', '').replace('\xa0', ' ').strip().lower()
        if element_cleaned:
            lst_cleaned.append(element_cleaned)

    return lst_cleaned


def parse_salary(salary_list: list):
    min_salary = None
    max_salary = None
    currency = None

    if not salary_list:
        return None, None, None

    salary_list = clean_list(salary_list)

    for i in range(len(salary_list)):
        if salary_list[i] == 'от' and i + 1 < len(salary_list):
            min_salary = salary_list[i + 1]
        elif salary_list[i] == 'до' and i + 2 < len(salary_list):
            max_salary = salary_list[i + 1]
            currency = salary_list[i + 2]

    if min_salary is None and max_salary is None:
        if salary_list[0].isdigit():
            min_salary = max_salary = salary_list[0]
        else:
            salary_range = salary_list[0].replace(' ', '')
            min_salary, max_salary = salary_range.split('–')

        if 1 < len(salary_list):
            currency = salary_list[1]
        else:
            currency = None

    return min_salary, max_salary, currency


def parse_currency(currency: str):
    if not currency:
        return None

    currency_dict = {
        '₽': 'RUB',
        '$': 'USD',
        '€': 'EUR',
        '₸': 'KZT',
        'Br': 'BYN',
    }

    return currency_dict.get(currency, None)


def clean_url(url: str):
    if not url:
        return None
    return url.split('?', 1)[0]


def extract_city(address: str):
    if not address:
        return None
    return address.split(',', 1)[0]


def convert_to_number(string: str):
    try:
        return int(string)
    except (ValueError, TypeError):
        return None


def parse_vacanscies(position: str, pages_quantity: int):
    vacancies_list = []

    for page_num in range(pages_quantity):
        page = get_vacancies_hh(position, page_num)

        tree = html.fromstring(page)
        vacancies = tree.xpath("//div[@data-qa='vacancy-serp__vacancy']")

        for vacancy in vacancies:
            title = vacancy.xpath(
                ".//span[@data-qa='serp-item__title-text']/text()")[0]

            salary_list = vacancy.xpath(
                ".//span[@class='magritte-text___pbpft_4-3-3 magritte-text_style-primary___AQ7MW_4-3-3 magritte-text_typography-label-1-regular___pi3R-_4-3-3']/text()")

            min_salary, max_salary, currency = parse_salary(salary_list)
            min_salary = convert_to_number(min_salary)
            max_salary = convert_to_number(max_salary)

            currency_normalize = parse_currency(currency)

            url = vacancy.xpath(".//a[@data-qa='serp-item__title']/@href")[0]
            url_cleared = clean_url(url)

            address = vacancy.xpath(
                ".//span[@data-qa='vacancy-serp__vacancy-address']/text()")[0]
            city = extract_city(address)

            vacancies_list.append({
                'Title': title,
                'Min salary': min_salary,
                'Max salary': max_salary,
                'Currency': currency_normalize,
                'City': city,
                'URL': url_cleared,
                'Source': 'hh.ru'
            })

    return vacancies_list


def get_collection_mongodb(database_name: str, collection_name: str):
    client = MongoClient('')
    db = client[database_name]
    collection = db[collection_name]
    return collection


def save_vacancies_to_mongodb(vacancies_list: list):
    collection = get_collection_mongodb('my_database', 'vacancies')

    for new in vacancies_list:
        result = collection.update_one(
            {'URL': new['URL']},
            {'$set': new},
            upsert=True
        )
        print(result)


def search_vacancies_by_salary(min_salary: int):
    collection = get_collection_mongodb('my_database', 'vacancies')
    query = {
        '$or': [
            {'Min salary': {'$gte': min_salary, '$ne': None}},
            {'Max salary': {'$gte': min_salary, '$ne': None}}
        ]}

    result = collection.find(query)

    if not result:
        print('No vacancies found')
        return

    df = pd.DataFrame(result)
    df_format = df[['Title', 'Min salary', 'Max salary']]
    print(df_format)


def main():
    while True:
        print("\n----------Actions----------")
        print('1. Receiving and recording new vacancies')
        print('2. Search for vacancies by salary')
        print('3. Exit\n')

        action = input('Enter action: ')

        if action == '1':
            position = input('Enter position: ')
            if not position:
                print('Empty value position is not allowed')
                continue

            pages_quantity = input('Enter quantity page: ')
            pages_quantity = convert_to_number(pages_quantity)
            if pages_quantity is None or pages_quantity <= 0:
                print('Incorrect pages quantity value')
                continue
            vacancies = parse_vacanscies(position, int(pages_quantity))
            save_vacancies_to_mongodb(vacancies)

        elif action == '2':
            min_salary = input('Enter minimum salary: ')
            min_salary = convert_to_number(min_salary)
            if min_salary is None:
                print('Incorrect salary value')
                continue

            search_vacancies_by_salary(min_salary)

        elif action == '3':
            print('Exit programm')
            break

        else:
            print('Invalid action')


if __name__ == '__main__':
    main()
