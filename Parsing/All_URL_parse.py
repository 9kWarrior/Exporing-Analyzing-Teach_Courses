import pandas as pd
from universities import universities
from waybackpy import WaybackMachineCDXServerAPI
from datetime import datetime


# Настройки
USER_AGENT = "Mozilla/5.0"  # User-Agent для обхода блокировки
START_YEAR = 2016           # Начальный год (включительно)
END_YEAR = 2024             # Конечный год (включительно)

def get_snapshots(url):
    """Получает список архивных копий URL за указанный период."""
    try:
        cdx_api = WaybackMachineCDXServerAPI(
            url,
            user_agent=USER_AGENT,
            start_timestamp=f"{START_YEAR}0101000000",  # Формат: ГГГГММДДЧЧММСС
            end_timestamp=f"{END_YEAR}1231235959",
        )
        snapshots = cdx_api.snapshots()
        return [{
            "url": url,
            "archive_url": s.archive_url,
            "date": s.timestamp,
        } for s in snapshots]
    except Exception as e:
        print(f"Ошибка для {url}: {e}")
        return []

# Сбор данных
all_snapshots = []
for url in universities:
    print(f"Проверяю {url}[0]...")
    snapshots = get_snapshots(url[0])
    all_snapshots.extend(snapshots)

# Сохранение в CSV
if all_snapshots:
    df = pd.DataFrame(all_snapshots)
    df.to_csv("university_snapshots.csv", index=False)
    print(f"Готово! Результаты сохранены в university_snapshots.csv")
else:
    print("Нет данных для сохранения.")