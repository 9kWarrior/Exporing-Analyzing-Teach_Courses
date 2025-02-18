import requests
import random
import time

def try_with_proxies(url, proxies_list, headers=None, timeout=10, max_retries=3):
    """
    Пытается выполнить GET-запрос к URL, используя прокси из списка.

    Args:
        url (str): URL для запроса.
        proxies_list (list): Список прокси в формате "IP:порт".
        headers (dict, optional): Заголовки запроса. Defaults to None.
        timeout (int, optional): Максимальное время ожидания запроса (в секундах). Defaults to 10.
        max_retries (int, optional): Максимальное количество попыток с разными прокси. Defaults to 3.

    Returns:
        requests.Response: Объект Response, если запрос успешен, иначе None.
    """

    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    for attempt in range(max_retries):
        proxy = random.choice(proxies_list)
        try:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",
            }
            print(f"Попытка {attempt + 1}/{max_retries} с прокси: {proxy}")
            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            print("Успешно!")
            return response  # Возвращаем Response, если запрос успешен
        except requests.exceptions.RequestException as e:
            print(f"Ошибка с прокси {proxy}: {e}")
            time.sleep(random.uniform(1, 3))  # Пауза перед следующей попыткой

    print(f"Не удалось выполнить запрос к {url} после {max_retries} попыток.")
    return None  # Возвращаем None, если все попытки неудачны


# Пример использования:
proxies = [
    "125.27.107.212:8080" # рабочий прокси
]

url_to_fetch = "https://www.avito.ru"  # Замените на нужный URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}  # Актуальный User-Agent

response = try_with_proxies(url_to_fetch, proxies, headers=headers)

if response:
    print("Содержимое страницы:")
    # print(response.text) # Раскомментируйте, чтобы увидеть HTML
else:
    print("Не удалось получить содержимое страницы.")

