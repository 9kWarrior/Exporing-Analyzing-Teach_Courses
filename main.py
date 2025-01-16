import csv
import numpy as np
import pandas as pd
data = pd.read_csv('../udemy_online_education_courses_dataset.csv', delimiter=',')
df = pd.DataFrame(data)
column_names = df.columns
selected_columns = ['price', 'level', 'subject']
df_selected = df[selected_columns]
print(df.shape)