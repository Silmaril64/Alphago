#!/bin/bash

mkdir -p ./data/RL/

for i in {0..1}
do
    python3 namedGame.py
    python3 _trainPolicyNetwork.py "./data/RL/" 0
done
