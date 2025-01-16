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

null_expl = null_data.explode('Format')
print(null_expl)