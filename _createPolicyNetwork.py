import gzip, os.path
import json
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Reshape
import numpy as np

model = Sequential([
    Conv2D(128, (5, 5), padding='same', activation = 'relu', data_format='channels_last', input_shape=(9,9,11)),
    Dropout(rate=0.5),
    BatchNormalization(),
    Conv2D(128, (3, 3), padding='same', activation = 'relu', data_format='channels_last'),
    Dropout(rate=0.5),
    BatchNormalization(),
    Conv2D(128, (3, 3), padding='same', activation = 'relu', data_format='channels_last'),
    Dropout(rate=0.5),
    BatchNormalization(),
    Conv2D(128, (3, 3), padding='same', activation = 'relu', data_format='channels_last'),
    Dropout(rate=0.5),
    BatchNormalization(),
    Flatten(),
    Dense(2048, activation = 'relu'),
    Dropout(rate=0.5),
    Dense(1024, activation = 'relu'),
    Dense(512, activation = 'relu'),
    Dense(256, activation = 'relu'),
    Dense(81, activation = 'softmax')
])

model.compile(loss='mse', optimizer='adam', metrics=['mse', 'mae'])
model.summary()
model.save('./models/policyNetwork')

print("Model Created Successfully")
