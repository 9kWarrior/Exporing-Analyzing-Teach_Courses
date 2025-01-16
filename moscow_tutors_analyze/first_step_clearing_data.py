import pandas as pd
import re
import numpy as np
from ast import literal_eval

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
audience_list