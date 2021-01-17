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
    Conv2D(64, 5, padding='same', activation = 'relu',    data_format='channels_first', input_shape=(9,9,11)),
    Conv2D(64, 3, padding='same', activation = 'relu',    data_format='channels_first'),
    Conv2D(64, 3, padding='same', activation = 'relu',    data_format='channels_first'),
    Conv2D(64, 3, padding='same', activation = 'relu',    data_format='channels_first'),
    Conv2D(64, 3, padding='same', activation = 'relu',    data_format='channels_first'),
    Flatten(),
    Dense(512, activation='relu'),
])

model.compile(loss='mse', optimizer='adam', metrics=['mse', 'mae'])
model.summary()
model.save('./models/fastPolicyNetwork')

print("Fast Policy Network Created Successfully")
