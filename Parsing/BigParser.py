from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import time


def extract_archive_date(url):
    """Извлекает дату из URL архивной версии"""
    try:
        # Ищем паттерн даты в URL (формат /web/YYYYMMDDHHMMSS/)
        date_str = re.search(r'/web/(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/', url)
        if date_str:
            year, month, day, hour, minute, second = date_str.groups()
            return f"{day}.{month}.{year} {hour}:{minute}:{second}"
        return "Дата не определена"
    except:
        return "Дата не определена"


def setup_driver():
    """Настройка Selenium WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


def clean_numeric_value(text):
    """Очистка числовых значений, замена прочерков на 0"""
    if not text or text.strip() == '—':
        return 0
    try:
        return float(re.sub(r'[^\d.]', '', text.strip()))
    except:
        return 0


def parse_program(program_block):
    """Парсинг данных одной программы"""
    data = {
        'Программа': np.nan,
        'Уровень': np.nan,
        'Факультет': np.nan,
        'Проходной балл': 0,  # По умолчанию 0 вместо NaN
        'Бюджетные места': 0,  # По умолчанию 0 вместо NaN
        'Стоимость': 0  # По умолчанию 0 вместо NaN
    }

    try:
        # Название программы
        name_tag = program_block.find('h3', class_='search-results-title')
        if name_tag:
            data['Программа'] = name_tag.get_text(strip=True)

        # Уровень образования
        level_tag = program_block.find('div', class_='fs-small')
        if level_tag:
            data['Уровень'] = level_tag.get_text(strip=True)

        # Факультет
        faculty_tag = program_block.find('h4', class_='search-results-info-big')
        if faculty_tag:
            data['Факультет'] = faculty_tag.get_text(strip=True)

        # Числовые показатели
        options_div = program_block.find('div', class_='row')
        if options_div:
            # Проходной балл
            passing_div = options_div.find('section', class_='sro-point')
            if passing_div:
                score = passing_div.find('div', class_='big-number-h2')
                if score:
                    data['Проходной балл'] = clean_numeric_value(score.get_text())

            # Бюджетные места
            budget_div = options_div.find('section', class_='sro-place')
            if budget_div:
                places = budget_div.find('div', class_='big-number-h2')
                if places:
                    data['Бюджетные места'] = int(clean_numeric_value(places.get_text()))

            # Стоимость
            price_div = options_div.find('section', class_='sro-price_interval')
            if price_div:
                price = price_div.find('div', class_='big-number-h2')
                if price:
                    data['Стоимость'] = clean_numeric_value(price.get_text())

    except Exception as e:
        print(f"Ошибка парсинга программы: {str(e)}")

    return data


def parse_ucheba_page(url):
    print("🚀 Запускаем парсинг с Selenium...")
    driver = setup_driver()
    results = []
    archive_date = extract_archive_date(url)  # Извлекаем дату архивации

    try:
        # Загрузка страницы с обработкой таймаута
        try:
            driver.get(url)
        except:
            print("⚠️ Превышено время загрузки страницы, продолжаем...")

        print(f"⏳ Ожидаем загрузки элементов (архив от {archive_date})...")

        # Ожидание появления вузов
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'search-results-item')))
        except:
            print("⚠️ Не удалось загрузить список вузов")
            return pd.DataFrame()

        # Находим все вузы
        uni_blocks = driver.find_elements(By.CLASS_NAME, 'search-results-item')
        print(f"🎓 Найдено вузов: {len(uni_blocks)}")

        for i, uni in enumerate(uni_blocks[:20]):
            try:
                # Прокручиваем к вузу
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", uni)
                time.sleep(2)

                # Название вуза
                try:
                    uni_name = uni.find_element(By.CLASS_NAME, 'search-results-title').text
                    uni_name = re.sub(r'\s+', ' ', uni_name).strip()
                    print(f"\n🏛 Вуз {i + 1}: {uni_name}")
                except:
                    print(f"⚠️ Не удалось получить название вуза #{i + 1}")
                    continue

                # Раскрытие списка программ
                try:
                    show_programs_btn = WebDriverWait(uni, 15).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'js-search-results-more-info')))
                    print(f"🔄 Найдена кнопка: {show_programs_btn.text}")

                    driver.execute_script("arguments[0].click();", show_programs_btn)
                    print("⏳ Ожидаем загрузки программ...")
                    time.sleep(5)

                    WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, 'search-results-info-item')))
                except:
                    print("⚠️ Не удалось раскрыть программы")
                    continue

                # Парсинг программ
                try:
                    programs_html = uni.find_element(By.CLASS_NAME, 'search-results-info').get_attribute('outerHTML')
                    soup = BeautifulSoup(programs_html, 'html.parser')
                    programs = soup.find_all('section', class_='search-results-info-item')
                    print(f"📚 Найдено программ: {len(programs)}")

                    for program in programs:
                        program_data = parse_program(program)
                        program_data.update({
                            'Вуз': uni_name,
                            'Дата архивации': archive_date  # Добавляем дату архивации
                        })
                        results.append(program_data)
                        print(f"   ✅ {program_data['Программа']} | Дата: {archive_date}")
                except Exception as e:
                    print(f"⚠️ Ошибка парсинга программ: {str(e)}")

            except Exception as e:
                print(f"❌ Ошибка обработки вуза #{i + 1}: {str(e)}")
                continue

        return pd.DataFrame(results)

    finally:
        try:
            driver.quit()
        except:
            pass


# Запуск парсера
try:
    test_url = "https://web.archive.org/web/20160213233521/https://www.ucheba.ru/for-abiturients/vuz"
    print(f"\n🌐 Загружаем данные с: {test_url}")
    df = parse_ucheba_page(test_url)

    if not df.empty:
        # Дополнительная очистка данных
        df = df.dropna(subset=['Программа'])

        # Замена оставшихся NaN (если есть) на 0 для числовых колонок
        numeric_cols = ['Проходной балл', 'Бюджетные места', 'Стоимость']
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Сохранение
        df.to_csv('ucheba_programs_final.csv', index=False, encoding='utf-8-sig')

        print("\n✅ Успешно собрано программ:", len(df))
        print("\nПример данных:")
        print(df.head().to_markdown(index=False, tablefmt="grid"))
    else:
        print("\n❌ Не удалось собрать данные")
except Exception as e:
    print(f"🔥 Критическая ошибка: {str(e)}")