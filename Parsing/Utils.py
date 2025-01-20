import requests
from bs4 import BeautifulSoup
import time
import csv
url = "https://www.avito.ru/moskva/predlozheniya_uslug/obuchenie_kursy/predmeti_shkoli_i_vuza-ASgBAgICAkSYC7afAaQrkrgC?cd=1&q=%D1%80%D0%B5%D0%BF%D0%B5%D1%82%D0%B8%D1%82%D0%BE%D1%80+%D0%BF%D0%BE+%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B5"  # Пример ссылки на Авито


def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        print("Страница загружена успешно")
    else:
        print(f"Ошибка загрузки страницы: {response.status_code}")
    response.encoding = 'utf-8'  # Задаем кодировку явно
    html_content = response.text
    return html_content


def parse_page_for_price(html_content):
    # Парсинг html с помощью BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    price_div = soup.find_all('div', class_='price-price-j2OjU')

    for item4 in price_div:
        # 2. Находим тег strong с классом 'styles-module-root-LEIrw' внутри price_div
        strong_tag = item4.find_all('strong', class_='styles-module-root-LEIrw')

        for item in strong_tag:
            # 3. Находим тег span внутри тега strong
            span_tag = item.find('span')

            if span_tag:
                price_text = span_tag.text.strip()
                print(f"Цена с текстом: {price_text}")

                # Извлекаем цену, обрабатывая случаи с "от" и без него
                parts = price_text.split()
                if "от" in parts:
                    # если есть "от", то берем следующий элемент
                    price_only = parts[1]
                else:
                    # иначе просто берем первый элемент
                    price_only = parts[0]
                if len(price_only) < 2:
                    if "от" in parts:
                        price_only = parts[1] + parts[2]
                    else:
                        price_only = parts[0] + parts[1]
                print(f"Цена: {price_only}")
    # return list_of_ads # список словарей


def save_to_csv(data, filename):
    # Сохранение данных в CSV файл
     with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


html = get_page_content(url)
parse_page_for_price(html)