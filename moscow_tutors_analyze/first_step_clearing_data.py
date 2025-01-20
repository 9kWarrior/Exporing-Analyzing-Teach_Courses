import pandas as pd
import re
import numpy as np
from ast import literal_eval
from util import replace_matches_in_column

pd.set_option('display.max_columns', 12) # Показать все колонки
pd.set_option('display.max_rows', None) # Показать все строки
pd.set_option('display.width', 1000) # Увеличить ширину вывода
pd.set_option('display.colheader_justify', 'center') # Выравнивание заголовков
pd.set_option('display.precision', 2) # Точность чисел


data = pd.read_csv(r"C:\Users\THUNDEROBOT\PycharmProjects\deeplom\repititors_price.csv")


# print(data.shape)
# print(data.head())
# print(data.isnull().sum())


bad_columns = ['Reviews_number', 'Experience', 'Status', 'Location', 'Tags', 'Audience', 'Video_presentation', 'Photo']
null_data = data[data.isnull().any(axis=1)]
# print(null_data)
null_data['Format'] = null_data['Format'].apply(lambda s: str(s).replace("at the tutor's","tutors place"))
null_data['Format'] = null_data['Format'].apply(lambda s: str(s).replace("at the student's","students place"))
for i in ['Categories', 'Format']:
    null_data[i] = null_data[i].apply(lambda s: list(literal_eval(str(s))) if s != np.nan else s)
df = pd.DataFrame(data)
column_names = df.columns
print(column_names)
data_selected = df.drop(['Reviews_number', 'Experience', 'Status', 'Location', 'Tags', 'Audience', 'Video_presentation', 'Photo'], axis = 1)
print(data_selected.shape)
print(data_selected.head())

preproccessed_data = data.copy()
preproccessed_data[['Reviews_number', 'Experience']] = preproccessed_data[['Reviews_number', 'Experience']].fillna(0)
preproccessed_data['Status'] = preproccessed_data['Status'].fillna('-')
preproccessed_data[['Location', 'Tags']] = preproccessed_data[['Location', 'Tags']].fillna('[]')
preproccessed_data['Audience'] = preproccessed_data['Audience'].fillna('[\'All\']')
preproccessed_data[['Video_presentation', 'Photo']] = preproccessed_data[['Video_presentation', 'Photo']].fillna('No')

# print(preproccessed_data.isnull().sum().sum())

cols_with_lists = ['Categories', 'Format', 'Location', 'Tags', 'Audience']
preproccessed_data['Format'] = preproccessed_data['Format'].apply(lambda s: str(s).replace("at the tutor\'s", "tutors place"))
preproccessed_data['Format'] = preproccessed_data['Format'].apply(lambda s: str(s).replace("at the student\'s", "students place"))
preproccessed_data['Location'] = preproccessed_data['Location'].apply(lambda s: str(s).replace("[\'", '[\"'))
preproccessed_data['Location'] = preproccessed_data['Location'].apply(lambda s: str(s).replace("\']", '\"]'))
preproccessed_data['Location'] = preproccessed_data['Location'].apply(lambda s: str(s).replace("\', \'", '\", \"'))


for i in cols_with_lists:
    preproccessed_data[i] = preproccessed_data[i].apply(lambda s: list(literal_eval(str(s))) if s != np.nan else s)
categories_series = preproccessed_data['Categories'].explode()
# print(preproccessed_data)
audience_series = preproccessed_data['Audience'].explode()
audience_list = audience_series.unique()


for i in ['11', '10']:
    replace_matches_in_column(df=preproccessed_data, col='Audience', string_to_match=i, replacing='Pupils of 10-11 grades', min_ratio=17)
for i in ['9', '8', '7', '6', '5']:
    replace_matches_in_column(df=preproccessed_data, col='Audience', string_to_match=i, replacing='Pupils of 5-9 grades', min_ratio=10)
replace_matches_in_column(df=preproccessed_data, col='Audience', string_to_match='4', replacing='Pupils of 1-4 grades', min_ratio=10)
for i in ['3', '2']:
    replace_matches_in_column(df=preproccessed_data, col='Audience', string_to_match='Pupils of ' + i, replacing='Pupils of 1-4 grades', min_ratio=71)
replace_matches_in_column(df=preproccessed_data, col='Audience', string_to_match='Children 1-3 года', replacing='Children 1-3 years old', min_ratio=100)

audience_series = preproccessed_data['Audience'].explode()
audience_list = audience_series.unique()
print(audience_list)
preproccessed_data = preproccessed_data.join(pd.crosstab(audience_series.index, audience_series))
preproccessed_data = preproccessed_data.drop(cols_with_lists, axis=1)


status_coding = {'Private tutor': '4', 'School teacher': '2', 'Postgraduate student': '3',
       'Native speaker': '6', 'University professor': '5', 'Student': '1', '-': '0'}

#Заменяем не цифровые данные на цифровые

for elem in status_coding:
    preproccessed_data['Status'] = preproccessed_data['Status'].apply(lambda x: (str(x).replace(elem, status_coding[elem])))
for i in ['Video_presentation', 'Photo']:
    preproccessed_data[i] = preproccessed_data[i].apply(lambda x: 1 if str(x) == 'Yes' else 0)

for i in ['Status', 'Reviews_number', 'Experience']:
    preproccessed_data = preproccessed_data.astype({i: 'int64'})

preproccessed_data.to_csv('first_tutor_data_postprocesed.csv', index=False)
