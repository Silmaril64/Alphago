#!/bin/bash

if [ $1 = 1 ]
then
        python3 _createFastPolicyNetwork.py
	python3 _createStrongPolicyNetwork.py
fi

if [ $2 = 1 ]
then
        ./_generateGames.sh
fi

if [ $3 = 1 ]
then
        ./_trainPolicyNetwork.sh
fi

if [ $4 = 1 ]
then
        ./_RLTrain.sh
fi