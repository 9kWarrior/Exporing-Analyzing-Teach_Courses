import csv
import numpy as np
from sklearn.metrics import make_scorer, mean_absolute_error
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


my_model_1 = XGBRegressor(n_estimators=500, learning_rate=0.05, n_jobs=4, max_depth=5)
my_model_1.fit(X_train, y_train,  eval_set=[(X_test, y_test)], verbose=False)


preds_1 = my_model_1.predict(X_test)
print("Mean Absolute Error: " + str(mean_absolute_error(preds_1, y_test)))


my_model_2 = RandomForestRegressor(max_depth=10, max_leaf_nodes=100, n_jobs=4)
my_model_2.fit(X_train, y_train)
#
#
# scores = -1 * cross_val_score(my_model_1, X, y, cv=5, scoring='neg_mean_absolute_error')
mae_scorer = make_scorer(mean_absolute_error)
scores = cross_val_score(my_model_2, X_train, y_train, cv=5, scoring=mae_scorer)
print("Cross-validation scores:", scores)
print("Mean cross-validation score:", scores.mean())
print("Standard deviation of cross-validation score", scores.std())
#
# print(scores)
# print("Average MAE score (across experiments):" + str(scores.mean()))

data_for_predictions = pd.DataFrame(np.array([[21,25,5,0,1,
                                              0,0,0,0,0,
                                              1,1,1,1]]),
                                    columns=X.columns)
pred_price = my_model_1.predict(data_for_predictions)
print(pred_price)