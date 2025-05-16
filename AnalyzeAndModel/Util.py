import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

#  Первичный анализ данных (без изменений)
def load_and_explore_data(file_path):
    df = pd.read_csv(
    file_path,
    parse_dates=['Дата архивации'],
    date_parser=lambda x: pd.to_datetime(x, format='%d.%m.%Y %H:%M:%S')
)
    print("=== Первые 5 строк ===")
    print(df.head())
    print("\n=== Информация о данных ===")
    print(df.info())
    print("\n=== Статистика числовых колонок ===")
    print(df.describe())
    cat_cols = ['Программа', 'Уровень', 'Факультет', 'Вуз']
    for col in cat_cols:
        print(f"\n=== Уникальные значения в '{col}' ({df[col].nunique()} шт.) ===")
        print(df[col].value_counts().head(10))
    return df

#  Очистка данных (УДАЛЕНИЕ строк с пропусками)
def clean_data(df):
    # Сохраняем исходное количество строк
    original_rows = df.shape[0]

    # Удаление ВСЕХ строк, где есть хотя бы один пропуск
    df_clean = df.dropna(how='any')

    # Удаление выбросов в 'Стоимость' (верхние 1%)
    upper_limit = df_clean['Стоимость'].quantile(0.99)
    df_clean = df_clean[df_clean['Стоимость'] <= upper_limit]

    # Отчёт о потерянных данных
    cleaned_rows = df_clean.shape[0]
    print(f"\nУдалено строк с пропусками: {original_rows - cleaned_rows}")
    print(f"Осталось строк: {cleaned_rows} ({cleaned_rows/original_rows:.1%} от исходных)")

    return df_clean

#  Feature Engineering
def prepare_features(df):
    df = df.drop(['Дата архивации'], axis=1)
    df['Бюджет_на_место'] = df['Бюджетные места'] / df['Проходной балл'].replace(0, 1)

    # One-Hot для 'Уровень'
    ohe_cols = ['Уровень']
    df = pd.get_dummies(df, columns=ohe_cols)

    # Label Encoding для остальных категорий
    from sklearn.preprocessing import LabelEncoder
    le_cols = ['Программа', 'Факультет', 'Вуз']
    for col in le_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    # Нормализация числовых признаков
    num_cols = ['Проходной балл', 'Бюджетные места', 'Бюджет_на_место']
    scaler = StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])

    return df
