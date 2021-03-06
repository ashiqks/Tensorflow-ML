# -*- coding: utf-8 -*-
"""LinearClassifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vmB59iPj3gOgxCh9FEfDOacbw61PV_JC

A program to run tensorflow's linear classifier using the estimator API, enhancing the feature selection by using feature_column module of tensorflow and 
feeding the data using tensorflow's pandas function.
"""

# import necessary packages
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import tensorflow as tf
import itertools
import numpy as np
import requests
import os
import gzip
import shutil

# Set ipython's max row display
pd.set_option('display.max_row', 1000)

# Set iPython's max column width to 50
pd.set_option('display.max_columns', 50)

# download the dataset and extract it 
f = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/covtype/covtype.data.gz")

with open('g.gz', 'wb') as fs:
  for chunks in f.iter_content(chunk_size=128):
    fs.write(chunks)

with gzip.open("g.gz", 'rb') as f_in:
    with open('covtype.csv', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

#!wget https://archive.ics.uci.edu/ml/machine-learning-databases/covtype/covtype.data.gz
#!gunzip covtype.data.gz
#!mv covtype.data covtype.csv

# read the dataset
df = pd.read_csv('covtype.csv')

# extract the only needed columns using the column names, here the column names are given by numbers
cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 54]
df = df[df.columns[cols]]
# assign new column names to extracted dataset
column_names = ['elevation', 'aspect', 'slope', 'hd_to_hydrology', 'vd_to_hydrology', 'hd_to_roadways', 
                'hillshade_9am', 'hillshade_noon', 'hillshade_3pm', 'hd_to_firepoints', 'cover_type']
df.columns = column_names

# shuffle the data and reset the index
df.sample(frac=1).reset_index(drop=True)

# print the first 5 rows of the dataframe
print(df.head())

# get the information regarding the dataframe
print(df.info())

# get the statistics of the data 
print(df.describe().transpose())

# plot the boxplot using seaborn
sns.set(style='ticks')
sns.boxplot(data=df)

# plot the pairplot of the dataframe
sns.pairplot(data=df)

# compute the correlation among the features in the dataset
corr_data = df.corr(method='pearson')
print(corr_data)

# plot the correlation matrix data using matplotlib
plt.matshow(corr_data)
plt.xticks(range(len(corr_data.columns)), corr_data.columns)
plt.yticks(range(len(corr_data.columns)), corr_data.columns)
plt.colorbar()
plt.show()

# define the columns to get scaled 
df_subcategories = df.loc[:, df.columns.isin(['aspect', 'slope', 'hillshade_9am', 'hillshade_noon', 'hillshade_3pm'])]

# instantiate contructor for the MinMaxScaler for the independent variables
x_scaler = MinMaxScaler()
#fit and transform the data 
df_scaled = x_scaler.fit_transform(df_subcategories)
df.loc[:, df.columns.isin(['aspect', 'slope', 'hillshade_9am', 'hillshade_noon', 'hillshade_3pm'])] = df_scaled

print(df.head())

# define the various feature column names
continuous_columns = ['aspect', 'slope', 'hillshade_9am', 'hillshade_noon', 'hillshade_3pm']
bucketized_columns = ['elevation', 'hd_to_hydrology', 'vd_to_hydrology', 'hd_to_roadways', 'hd_to_firepoints']
crossed_columns = [('hd_to_hydrology', 'vd_to_hydrology'), ('hillshade_9am', 'hillshade_noon', 'hillshade_3pm')]

# convert the continous columns into numeric feature columns
continuous_cols = [tf.feature_column.numeric_column(c) for c in continuous_columns]
print(continuous_cols)

# for bucketizing the columns first convert the column into numeric feature column and then into a bucketized feature column with the boundaries set in the 'boundaries' parameter 
bucketized_cols = [tf.feature_column.numeric_column(c) for c in bucketized_columns]

elevation_buckt_cols = tf.feature_column.bucketized_column(source_column=bucketized_cols[0], boundaries=[i for i in range(1800, 4000, 100)])
print(elevation_buckt_cols)

hd_to_hydrology_buckt_cols = tf.feature_column.bucketized_column(source_column=bucketized_cols[1], boundaries=[i for i in range(0, 1500, 100)])
print(hd_to_hydrology_buckt_cols)

vd_to_hydrology_buckt_cols = tf.feature_column.bucketized_column(source_column=bucketized_cols[2], boundaries=[i for i in range(-180, 700, 100)])
print(vd_to_hydrology_buckt_cols)

hd_to_roadways_buckt_cols = tf.feature_column.bucketized_column(source_column=bucketized_cols[3], boundaries=[i for i in range(0, 8000, 100)])
print(hd_to_roadways_buckt_cols)

hd_to_firepoints_buckt_cols = tf.feature_column.bucketized_column(source_column=bucketized_cols[4], boundaries=[i for i in range(0, 8000, 100)])
print(hd_to_firepoints_buckt_cols)

buckt_cols = [elevation_buckt_cols, hd_to_hydrology_buckt_cols, vd_to_hydrology_buckt_cols, hd_to_roadways_buckt_cols, hd_to_firepoints_buckt_cols]

# convert the columns to crossed feature columns
hydrology_crossed_cols = tf.feature_column.crossed_column([hd_to_hydrology_buckt_cols, vd_to_hydrology_buckt_cols], hash_bucket_size=1000)
print(hydrology_crossed_cols)

hillshade_crossed_cols = tf.feature_column.crossed_column(['hillshade_9am', 'hillshade_noon', 'hillshade_3pm'], hash_bucket_size=500)
print(hillshade_crossed_cols)

crossed_cols = [hydrology_crossed_cols, hillshade_crossed_cols]

# check if any null values are present in the dataset
df.columns.isnull().sum()

# split dataset into train, test and prediction sets
train_data = df.iloc[:int(0.8*len(df)), :]
test_data = df.iloc[int(0.8*len(df)):int(0.98*len(df)),:]
prediction_data = df.iloc[int(0.98*len(df)):, :]
print(train_data.shape, test_data.shape, prediction_data.shape)

cols = list(df.columns)
LABEL = cols.pop(-1)
FEATURES = cols
print(cols)
print('FEATURES: ',FEATURES)
print('LABEL: ', LABEL)

# instantiate linear classifier estimator object with the feature columns defined earlier and the model directory
estimator = tf.estimator.LinearClassifier(feature_columns=continuous_cols+buckt_cols+crossed_cols, n_classes=8)

# define the input function to be parsed for training, evaluating and predicting
def get_input_fn(data, num_epochs=None, n_batch=128, shuffle=True):
  return tf.estimator.inputs.pandas_input_fn(
  x= pd.DataFrame({d: data[d].values for d in FEATURES}),
  y= pd.Series(data[LABEL].values),
  batch_size=n_batch,
  num_epochs=num_epochs,
  shuffle=shuffle
  )

# train the estimator model
estimator.train(input_fn=get_input_fn(train_data, num_epochs=1, n_batch=128, shuffle=True))

# evaluate the estimator model using test data
ev = estimator.evaluate(input_fn=get_input_fn(test_data, num_epochs=1, n_batch=128, shuffle=False))

# print the evaluation loss
loss = ev['loss']
print('Loss: ', loss)

# find the prediction results using the prediction data
y_hat = estimator.predict(input_fn=get_input_fn(prediction_data, num_epochs=1, n_batch=128, shuffle=True))

# enumerate through the predicted result to get the predictions 
for y in enumerate(y_hat):
  print(y)

# iterate over the predicted results
predictions = [np.argmax(p['probabilities']) for p in itertools.islice(y_hat, prediction_data.shape[0])]
print(predictions)