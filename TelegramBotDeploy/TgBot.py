import pandas as pd
universities_df = pd.read_csv('programs_names_data.csv')
print(universities_df)
UNIVERSITIES = universities_df['Программа'].tolist()  # Предполагаем столбец 'Название'
print(UNIVERSITIES)
