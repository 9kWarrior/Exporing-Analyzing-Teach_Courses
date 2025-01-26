import csv
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor


data = pd.read_csv(r"C:\Users\THUNDEROBOT\PycharmProjects\deeplom\Exporing-Analyzing-Teach_Courses\moscow_tutors_analyze\first_tutor_data_postprocesed.csv")
X = data[data['Score'] >= 4.0].drop(['Price', 'Score'], axis=1)
y = data[data['Score'] >= 4.0].Price
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
print(X_train.shape)
