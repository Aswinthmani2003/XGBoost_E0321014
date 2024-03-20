# -*- coding: utf-8 -*-
"""XGBoost.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1McOd9WTdtQZH1U7n2kVLgZUQwUjvg1dL
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import xgboost as xgb
from sklearn.metrics import mean_squared_error
color_pal = sns.color_palette()
plt.style.use('fivethirtyeight')

df = pd.read_csv('PJME_hourly.csv')
df = df.set_index('Datetime')
df.index = pd.to_datetime(df.index)

df.plot(style='.',
figsize=(15, 5),
color=color_pal[0],
title='PJME Energy Use in MW')
plt.show()

# Train Test Split
train = df.loc[df.index < '01-01-2015']
test = df.loc[df.index >= '01-01-2015']
train = df.loc[df.index < '01-01-2015']
test = df.loc[df.index >= '01-01-2015']
fig, ax = plt.subplots(figsize=(15, 5))
train.plot(ax=ax, label='Training Set', title='Data Train/Test Split')
test.plot(ax=ax, label='Test Set')
ax.axvline('01-01-2015', color='black', ls='--')
ax.legend(['Training Set', 'Test Set'])
plt.show()

fig, ax = plt.subplots(figsize=(15,5))
sns.lineplot(data=df.loc[(df.index > '2010-01-01') & (df.index < '2010-01-08')])
plt.title('Week Of Data')
plt.show()

def create_features(df):
  df = df.copy()
  df['hour'] = df.index.hour
  df['dayofweek'] = df.index.dayofweek
  df['quarter'] = df.index.quarter
  df['month'] = df.index.month
  df['year'] = df.index.year
  df['dayofyear'] = df.index.dayofyear
  df['dayofmonth'] = df.index.day
  df['weekofyear'] = df.index.isocalendar().week
  return df

df = create_features(df)
fig, ax = plt.subplots(figsize=(15,5))
sns.boxplot(df,x='hour',y='PJME_MW')
ax.set_title('MW By Hour')

fig, ax = plt.subplots(figsize=(15,5))
sns.boxplot(df,x='month',y='PJME_MW')
ax.set_title('MW By Month')

train = create_features(train)
test = create_features(test)
FEATURES = ['hour','dayofweek','month','quarter','dayofyear','year','dayofmonth','weekofyear']
TARGET= 'PJME_MW'
X_train = train[FEATURES]
y_train = train[TARGET]
X_test = test[FEATURES]
y_test = test[TARGET]
reg = xgb.XGBRegressor(n_estimators = 1000,early_stopping_rounds=50,learning_rate = 0.01)
reg.fit(X_train,y_train,eval_set=[(X_train,y_train),(X_test,y_test)])

feature_importances = pd.DataFrame(data=reg.feature_importances_,index = reg.feature_names_in_,columns=['importances'])
feature_importances = feature_importances.sort_values(by = 'importances',ascending=1)
feature_importances.plot(kind='barh')
plt.legend('')
plt.title('Features Importances')

test['prediciton'] = reg.predict(X_test)
plt.plot(test['PJME_MW'],label='True')
plt.plot(test['prediciton'],label='Prediction')
plt.legend()

df['PJME_MW'].plot()
test['prediciton'].plot()
plt.legend()

# Filtering data
filtered_data = test.loc[(test.index > '04-01-2018') & (test.index < '04-08-2018')]
# Plotting
plt.figure(figsize=(15, 5))
sns.lineplot(data=filtered_data['PJME_MW'], marker='o', label='Truth Data')
sns.scatterplot(data=filtered_data['prediciton'], marker='.', label='Prediction',color='red')
plt.title('Week Of Data')
plt.legend()
plt.show()

mean_squared_error(test['PJME_MW'],test['prediciton'])
13972551.445122646
test['error'] = test['PJME_MW'] - test['prediciton']
test['abs_error'] = test['error'].apply(np.abs)
error_by_day = test.groupby(['year','month','dayofmonth']) \
.mean()[['PJME_MW','prediciton','error','abs_error']]
# Over forecasted days
error_by_day.sort_values('error', ascending=True).head(10)

# Worst absolute predicted days
error_by_day.sort_values('abs_error', ascending=False).head(10)

# Best predicted days
error_by_day.sort_values('abs_error', ascending=True).head(10)

