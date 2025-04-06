import pandas as pd
from tqdm import tqdm
from BigParser import parse_ucheba_page
import os


def process_all_snapshots():
    # Список всех CSV файлов с архивными ссылками
    csv_files = [
        'university_s_20_snapshots.csv',
        'university_snapshots.csv',
        'university_s_40_snapshots.csv'
    ]

    all_results = []

    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"⚠️ Файл не найден: {csv_file}")
            continue

        print(f"\n🔍 Обработка файла: {csv_file}")

        try:
            # Читаем текущий CSV
            df_urls = pd.read_csv(csv_file)

            # Парсим все URL из файла
            for url in tqdm(df_urls['archive_url'], desc=f"Парсинг {os.path.basename(csv_file)}"):
                try:
                    df_page = parse_ucheba_page(url)
                    if not df_page.empty:
                        all_results.append(df_page)
                except Exception as e:
                    print(f"❌ Ошибка при обработке {url}: {str(e)}")
                    continue

        except Exception as e:
            print(f"⚠️ Ошибка чтения файла {csv_file}: {str(e)}")
            continue

    # Объединяем все результаты
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)

        # Сохраняем результаты
        output_file = 'combined_universities_data.csv'
        final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n🎉 Готово! Все данные сохранены в {output_file}")
        print(f"Всего обработано университетов: {len(final_df)}")

        return final_df
    else:
        print("\n⚠️ Не удалось собрать данные ни по одному университету")
        return pd.DataFrame()


# Пример использования
if __name__ == "__main__":
    final_data = process_all_snapshots()
    if not final_data.empty:
        print("\nПример данных:")
        print(final_data.head().to_markdown(index=False, tablefmt="grid"))