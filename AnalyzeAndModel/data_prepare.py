import pandas as pd
from datetime import datetime
from Util import load_and_explore_data, clean_data, prepare_features

# Загрузка данных
file_path = r"C:\Users\User\PycharmProjects\deeplom\all_universities_data_s_0_0_200.csv"
df = load_and_explore_data(file_path)
df_clean = clean_data(df)
# df = df[(df['Стоимость'] >= 60000) & (df['Стоимость'] <= 550000)]
df = df.sort_values('Дата архивации')  # Важно: сортировка по дате!

# Пример данных после сортировки:
print(df[['Дата архивации', 'Программа', 'Стоимость']].head())

df_time = df.groupby(['Дата архивации', 'Программа', 'Вуз']).agg({
    'Стоимость': 'mean',
    'Проходной балл': 'mean',
    'Бюджетные места': 'sum'
}).reset_index()

df['Дата архивации'] = pd.to_datetime(df['Дата архивации'], errors='coerce')  # 'coerce' превратит ошибки в NaT

# Проверка пропусков после преобразования
print("Пропуски в дате:", df['Дата архивации'].isna().sum())

missing_dates = df[df['Дата архивации'].isna()]

print(missing_dates.head(20))

missing_dates.to_csv('пропущенные_даты.csv', index=False, encoding='utf-8')

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt


# Преобразование даты в числовые признаки
df['Дата архивации'] = pd.to_datetime(df['Дата архивации'])
df['Год'] = df['Дата архивации'].dt.year
df['Месяц'] = df['Дата архивации'].dt.month
df['День'] = df['Дата архивации'].dt.day

# Выбор нужных признаков
features = ['Год', 'Месяц', 'День', 'Проходной балл', 'Бюджетные места', 'Программа', 'Вуз']
X = df[features]
y = df['Стоимость'].values.reshape(-1, 1)  # Преобразуем в 2D-массив

# Масштабируем целевую переменную
scaler_y = StandardScaler()
y_scaled = scaler_y.fit_transform(y)

# Разделяем признаки на числовые и категориальные
numerical_features = ['Год', 'Месяц', 'День', 'Проходной балл', 'Бюджетные места']
categorical_features = ['Программа', 'Вуз']

# Препроцессинг
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

X_processed = preprocessor.fit_transform(X)
X_processed_dense = X_processed.toarray() if hasattr(X_processed, 'toarray') else X_processed