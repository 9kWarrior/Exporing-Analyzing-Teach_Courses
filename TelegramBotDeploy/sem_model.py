import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
okso_df = pd.read_excel("okso.xlsx")
section_ii = okso_df.iloc[623:863]    # Раздел III
section_v = okso_df.iloc[1120:1283]   # Раздел V
filtered_okso = pd.concat([section_ii, section_v])
filtered_okso.columns = ['code', 'name', 'col3', 'col4']
filtered_okso = filtered_okso[filtered_okso['code'].astype(str).str.startswith(('2', '5'))]

from sentence_transformers import SentenceTransformer
import pandas as pd
import re
import numpy as np
from rapidfuzz import fuzz, process

# Загрузка модели
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# Подготовка данных
okso_names = filtered_okso['name'].str.lower().tolist()
okso_codes = filtered_okso['code'].tolist()
okso_embeddings = model.encode(okso_names)

from rapidfuzz import fuzz, process
import re

def find_exact_match(query, okso_names, okso_codes):
    query_clean = re.sub(r'[^\w\s]', '', query.lower()).strip()

    # Ищем полные совпадения с учетом границ слов
    for name, code in zip(okso_names, okso_codes):
        name_clean = re.sub(r'[^\w\s]', '', name.lower()).strip()

        # Только если запрос полностью совпадает с названием (целиком)
        if query_clean == name_clean:
            print(name, ' -- ', code)
            return code

        # Или если название состоит из запроса + дополнительных слов
        if re.fullmatch(rf"{re.escape(query_clean)}(?:\s+.+)?", name_clean):
            print(name, ' -- ', code)
            continue  # Пропускаем более длинные варианты
    return None

def find_okso_code(query):
    # Нормализация запроса
    query_norm = re.sub(r'[^\w\s]', '', query.lower()).strip()

    # 1. Жесткий поиск полных совпадений
    for name, code in zip(okso_names, okso_codes):
        name_norm = re.sub(r'[^\w\s]', '', name.lower()).strip()
        if query_norm == name_norm:
            return code

    # 2. Поиск через rapidfuzz (только если нет полного совпадения)
    fuzzy_match = process.extractOne(
        query_norm,
        okso_names,
        scorer=fuzz.token_set_ratio,
        score_cutoff=90
    )

    if fuzzy_match and fuzzy_match[1] >= 90:
        return okso_codes[okso_names.index(fuzzy_match[0])]

    # 3. Семантический поиск (как запасной вариант)
    query_embed = model.encode([query_norm])
    similarities = np.dot(okso_embeddings, query_embed.T).flatten()
    best_match_idx = np.argmax(similarities)
    if similarities[best_match_idx] > 0.7:
        return okso_codes[best_match_idx]

    return "Не найдено"