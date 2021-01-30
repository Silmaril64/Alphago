#!/bin/bash

for i in {0..1}
do
    python3 _trainPolicyNetwork.py "./data/gnugo/" 1
done
