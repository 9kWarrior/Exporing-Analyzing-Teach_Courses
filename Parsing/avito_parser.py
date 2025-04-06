import requests
from bs4 import BeautifulSoup
import time
import csv
proxies = {"http": "http://125.27.107.212:8080",
            "https": "http://125.27.107.212:8080"}
base_url = "https://www.avito.ru/moskva/predlozheniya_uslug/obuchenie_kursy/predmeti_shkoli_i_vuza-ASgBAgICAkSYC7afAaQrkrgC?cd=1&q=%D1%80%D0%B5%D0%BF%D0%B5%D1%82%D0%B8%D1%82%D0%BE%D1%80+%D0%BF%D0%BE+%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B5"
page_number = "1"
url = f"{base_url}&p={page_number}"
# url = "https://www.avito.ru/moskva/predlozheniya_uslug/obuchenie_kursy/predmeti_shkoli_i_vuza-ASgBAgICAkSYC7afAaQrkrgC?cd=1&p=2&q=%D1%80%D0%B5%D0%BF%D0%B5%D1%82%D0%B8%D1%82%D0%BE%D1%80+%D0%BF%D0%BE+%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B5"
def get_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',  # Может потребоваться обработка gzip
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',  # Важно, если пришли с Google
        'TE': 'Trailers',
    }
    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
    if response.status_code == 200:
        html_content = response.text
        print("Страница загружена успешно")
    else:
        print(f"Ошибка загрузки страницы: {response.status_code}")
    response.encoding = 'utf-8'  # Задаем кодировку явно
    html_content = response.text
    time.sleep(3)
    return html_content


def parse_page_for_price(html_content):
    # Парсинг html с помощью BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    all_users = soup.find_all('div', class_='items-items-pZX46')
    print(len(all_users))
    price_div = soup.find_all('div', class_='iva-item-root-Se7z4 photo-slider-slider-ZccM3 iva-item-list-CLaiS iva-item-redesign-H4ow9 iva-item-responsive-GCo6h items-item-Reit3 items-listItem-rKPls js-catalog-item-enum')
    total_price = []
    total_rating = []
    print(len(price_div))
    for item4 in price_div:
        # 2. Находим тег strong с классом 'styles-module-root-LEIrw' внутри price_div
        strong_tag = item4.find_all('strong', class_='styles-module-root-LEIrw')
        rating_tag = item4.find_all('div', class_='SellerRating-scoreAndStars-_ti2Y')

        for item in strong_tag:
            # 3. Находим тег span внутри тега strong
            span_tag = item.find('span')

            if span_tag:
                price_text = span_tag.text.strip()
                print(f"Цена с текстом: {price_text}")

                # Извлекаем цену, обрабатывая случаи с "от" и без него
                parts = price_text.split()
                if "Бесплатно" or "договорная" in parts:
                    # если есть "от", то берем следующий элемент
                    price_only = 0
                else:
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
                total_price.append(int(price_only))


        for item in rating_tag:
            score_element = soup.find('span', class_='styles-module-size_xs-ij5Ua',
                                      attrs={'data-marker': 'seller-rating/score'})
            if score_element:
                score = score_element.text  # Получить текст (значение) из элемента
                print(f"Score: {score}")
                total_rating.append(score)
            else:
                print("Элемент с оценкой не найден.")
                total_rating.append(score)

    print(total_rating)
    return total_price


def save_to_csv(data, filename):
    # Сохранение данных в CSV файл
     with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


for i in range(1000):
    url = f"{base_url}&p={page_number}"
    html = get_page_content(url)
    print(parse_page_for_price(html))
    page_number = str(int(page_number) + 1)
# print(parse_page_for_price(html))
