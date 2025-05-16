from Util import load_and_explore_data, clean_data, prepare_features

file_path = r"C:\Users\User\PycharmProjects\deeplom\all_universities_data_s_0_0_200.csv"
df = load_and_explore_data(file_path)
df_clean = clean_data(df)
df_final = prepare_features(df_clean)

print("\n=== Готовые данные ===")
print(df_clean.head())

import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
sns.histplot(df_clean['Стоимость'], kde=True, bins=30)
plt.title('Распределение стоимости обучения')
plt.xlabel('Стоимость (руб)')
plt.ylabel('Количество программ')
plt.show()

sns.barplot(data=df_clean, x='Уровень', y='Стоимость')
plt.title('Средняя стоимость: бакалавриат vs магистратура')
plt.xlabel('0 = Магистратура, 1 = Бакалавриат')
plt.ylabel('Средняя стоимость (руб)')
plt.show()

corr = df_clean.corr(numeric_only=True)['Стоимость'].sort_values(ascending=False)
print(corr)

top_faculties = df_clean['Факультет'].value_counts().nlargest(10).index
sns.boxplot(data=df_clean[df_clean['Факультет'].isin(top_faculties)], x='Факультет', y='Стоимость')
plt.xticks(rotation=45)
plt.title('Стоимость по топ-10 факультетам')
plt.show()

sns.scatterplot(data=df_clean, x='Бюджетные места', y='Стоимость')
plt.title('Зависимость стоимости от числа бюджетных мест')
plt.show()