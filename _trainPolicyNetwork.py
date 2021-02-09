import gzip, os.path
import json
from sklearn.model_selection import train_test_split
import tensorflow as tf
import tensorflow.keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Reshape
import numpy as np
from os import listdir
import random
import sys

def reconstruct_lists_from_string(s):
    """Je ne prend pas en compte les nombres à plus de 1 chiffre, car je n'en ai ici pas besoin;
    Je dois par contre prendre en compte les nombres négatifs"""
    res = []
    signe = 1
    final = []
    for i in range(len(s)):
        if s[i] == '[':
            if len(res) == 0:
                print(".", end="")
            res.append([])
        elif s[i] == ']':
            tempo = res.pop()
            if len(res) != 0:
                res[-1].append(tempo)
            else: 
                final.append(tempo)
        elif s[i] == '1' or s[i] == '0':
            res[-1].append(signe*int(s[i]))
            signe = 1
        elif s[i] == '-':
            signe = -1
        else: # Si espace ou virgule
            pass  
    return final

epochs = 1
batch_size = 1024

s_model = tensorflow.keras.models.load_model('./models/strongPolicyNetwork')
if int(sys.argv[2]) == 1:
    f_model = tensorflow.keras.models.load_model('./models/fastPolicyNetwork')       
    
file_list = os.listdir(sys.argv[1])

with open(sys.argv[1] + file_list[random.randint(0,len(file_list)-1)], 'r') as jsonfile:
#with open("./data/" + file_list[random.randint(0,len(file_list)-1)], 'r') as jsonfile:
    #data = json.load(jsonfile)
    data = jsonfile.read()
    data = reconstruct_lists_from_string(data)
    tempo = []
    # TODO TOCHECK
    for x in data:
        tempo += x
    data = tempo

# TODO TOCHECK
X_data = [data[i][0] for i in range(len(data)) ]
Y_data = [data[i][1] for i in range(len(data)) ]

X_train, X_test, Y_train, Y_test = train_test_split(X_data, Y_data, test_size=0.1)

X_train = np.asarray(X_train).astype(np.float32)
Y_train = np.asarray(Y_train).astype(np.float32)

history = s_model.fit(X_train,Y_train, 
                    batch_size=batch_size, 
                    epochs=epochs, verbose=2)

if int(sys.argv[2]) == 1:
    f_model.fit(X_train,Y_train, 
                    batch_size=batch_size, 
                    epochs=epochs, verbose=2)

s_model.save('./models/strongPolicyNetwork')

if int(sys.argv[2]) == 1:
    f_model.save('./models/fastPolicyNetwork')
