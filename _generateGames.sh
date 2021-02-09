#!/bin/bash

mkdir -p ./data/gnugo/

for i in {0..1}
do
    python3 _generateGames.py
done
