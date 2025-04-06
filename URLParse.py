import waybackpy
from waybackpy import WaybackMachineSaveAPI

# Сохраняем текущую страницу в архив (если её ещё нет)
save_api = WaybackMachineSaveAPI("https://www.ucheba.ru/for-abiturients/vuz", "my-user-agent")
save_api.save()

# Ищем архивные версии
from waybackpy import WaybackMachineCDXServerAPI

url = "https://www.ucheba.ru/for-abiturients/vuz"
user_agent = "Mozilla/5.0"

cdx_api = WaybackMachineCDXServerAPI(url, user_agent)
snapshots = cdx_api.snapshots()  # Все сохранённые копии
i = 0
for snapshot in snapshots:
    print(snapshot.archive_url)
    i += 1  # Ссылка на архивную версию
    print(snapshot.timestamp)    # Дата сохранения (например, 20220101)