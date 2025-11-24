import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient


def string_to_float(raiting: str):
    try:
        return float(raiting)
    except (ValueError, TypeError):
        return None


def parse_bonus(bonus: str):
    if not bonus:
        return None

    bonus = bonus.replace('+ ', '').replace(' ', '').strip()
    return int(bonus)


def parse_price(price: str):
    if not price:
        return None

    price = price.replace(' ', '').replace('₽', '').strip()
    return int(price)


def extract_info(web_elements):

    dict_products = []

    titles = web_elements.find_elements(
        By.XPATH, './/div[@class="product-mini-card__name"]//div[@class="title"]')
    base_prices = web_elements.find_elements(
        By.XPATH, './/div[@class="product-mini-card__price"]//span[@class="price__main-value"]')
    discounted_prices = web_elements.find_elements(
        By.XPATH, './/div[@class="product-mini-card__price"]//span[@class="price__sale-value"]')
    ratings = web_elements.find_elements(
        By.XPATH, './/mvid-star-rating[@class="stars-with-pointer"]//span[@class="value"]')
    bonuses = web_elements.find_elements(
        By.XPATH, './/div[@class="product-mini-card__bonus-rubles"]//div[@class="mbonus-block__count-br"]')

    lenght = len(titles)

    for i in range(lenght):
        title = titles[i].text
        base_price = parse_price(base_prices[i].text)
        discounted_price = parse_price(discounted_prices[i].text)
        rating = string_to_float(ratings[i].text)
        bonus = parse_bonus(bonuses[i].text)

        dict_products.append({
            'Title': title,
            'Base price': base_price,
            'Discounted price': discounted_price,
            'Rating': rating,
            'Bonus': bonus
        })

    return dict_products


def get_collection_mongodb(database_name: str, collection_name: str):
    client = MongoClient('')
    db = client[database_name]
    collection = db[collection_name]
    return collection


def save_products_to_mongodb(vacancies_list: list):
    collection = get_collection_mongodb('my_database', 'mvideo')

    for new in vacancies_list:
        result = collection.update_one(
            {'Title': new['Title']},
            {'$set': new},
            upsert=True
        )
        print(result)


def main():
    url = 'https://www.mvideo.ru/'

    chrome_options = Options()
    chrome_options.add_argument('start-maximized')
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    time.sleep(5)

    carousels = driver.find_elements(By.CLASS_NAME, 'mvid-carousel-inner')
    bestsellers = carousels[1]
    driver.execute_script(
        'arguments[0].scrollIntoView({block: "center"});', bestsellers)
    time.sleep(5)

    while True:
        try:
            next_button = WebDriverWait(bestsellers, 2).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//mvid-simple-product-collection[@class='page-carousel-padding']//button[@class='btn forward mv-icon-button--primary mv-icon-button--shadow mv-icon-button--medium mv-button mv-icon-button']"
                ))
            )
            next_button.click()
            time.sleep(1)
        except:
            break

    products = extract_info(bestsellers)
    save_products_to_mongodb(products)


if __name__ == '__main__':
    main()
