import pandas as pd
import re
import numpy as np

data = pd.read_csv(r"C:\Users\THUNDEROBOT\PycharmProjects\deeplom\repititors_price.csv")


# print(data.shape)
# print(data.head())
# print(data.isnull().sum())


bad_columns = ['Reviews_number', 'Experience', 'Status', 'Location', 'Tags', 'Audience', 'Video_presentation', 'Photo']
null_data = data[data.isnull().any(axis=1)]
# print(null_data)

df = pd.DataFrame(data)
column_names = df.columns
print(column_names)
data_selected = df.drop(['Reviews_number', 'Experience', 'Status', 'Location', 'Tags', 'Audience', 'Video_presentation', 'Photo'], axis = 1)
print(data_selected.shape)
print(data_selected.head())