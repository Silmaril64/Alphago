''' Sorry no comments :).
'''
import Goban 
import importlib
import time
from io import StringIO
import sys
import random
import numpy as np
import json
import os, signal    
from utils import prepare_datas

print("On commence la partie nommée")

def fileorpackage(name):
    if name.endswith(".py"):
        return name[:-3]
    return name


###############################

DATAS = []
VERB = False
LEARN = True

file_list = os.listdir('./data/RL/')
nb_files = len(file_list)
MAX_NB_FILES = 100

if (nb_files <= MAX_NB_FILES):
    file_name = './data/RL/RL_datas_' + str(nb_files + 1) + '.json'
else:
    file_name = './data/RL/RL_datas_' + str(random.randint(1, nb_files)) + '.json'


###############################
    

if len(sys.argv) > 2:
    classNames = [fileorpackage(sys.argv[1]), fileorpackage(sys.argv[2])]
elif len(sys.argv) > 1:
    classNames = [fileorpackage(sys.argv[1]), 'myPlayer']
else:
    classNames = ['_alphagoPlayer', '_alphagoPlayer']

b = Goban.Board()

players = []
player1class = importlib.import_module(classNames[0])
player1 = player1class.myPlayer()
player1.newGame(Goban.Board._BLACK)
players.append(player1)

player2class = importlib.import_module(classNames[1])
player2 = player2class.myPlayer()
player2.newGame(Goban.Board._WHITE)
players.append(player2)

totalTime = [0,0] # total real time for each player
nextplayer = 0
nextplayercolor = Goban.Board._BLACK
nbmoves = 1

outputs = ["",""]
sysstdout= sys.stdout
stringio = StringIO()
wrongmovefrom = 0

while not b.is_game_over():
    if VERB:
        print("Referee Board:")
        b.prettyPrint() 
        print("Before move", nbmoves)
    legals = b.legal_moves() # legal moves are given as internal (flat) coordinates, not A1, A2, ...
    if VERB:
        print("Legal Moves: ", [b.move_to_str(m) for m in legals]) # I have to use this wrapper if I want to print them
    nbmoves += 1
    print("Turn nb ", nbmoves - 1, flush = True)
    otherplayer = (nextplayer + 1) % 2
    othercolor = Goban.Board.flip(nextplayercolor)
    
    currentTime = time.time()
    #sys.stdout = stringio
    move = players[nextplayer].getPlayerMove() # The move must be given by "A1", ... "J8" string coordinates (not as an internal move)
    #sys.stdout = sysstdout
    #playeroutput = stringio.getvalue()
    #stringio.truncate(0)
    #stringio.seek(0)
    #print(("[Player "+str(nextplayer) + "] ").join(playeroutput.splitlines(True)))
    #outputs[nextplayer] += playeroutput
    totalTime[nextplayer] += time.time() - currentTime
    if VERB:
        print("Player ", nextplayercolor, players[nextplayer].getPlayerName(), "plays: " + move) #changed 

    if not Goban.Board.name_to_flat(move) in legals:
        print(otherplayer, nextplayer, nextplayercolor)
        print("Problem: illegal move")
        wrongmovefrom = nextplayercolor
        break
    b.push(Goban.Board.name_to_flat(move)) # Here I have to internally flatten the move to be able to check it.
    players[otherplayer].playOpponentMove(move)
 
    nextplayer = otherplayer
    nextplayercolor = othercolor

print("The game is over")
    
if VERB:
    
    b.prettyPrint()
    result = b.result()
    print("Time:", totalTime)
    print("GO Score:", b.final_go_score())
    print("Winner: ", end="")
    if wrongmovefrom > 0:
        if wrongmovefrom == b._WHITE:
            print("BLACK")
        elif wrongmovefrom == b._BLACK:
            print("WHITE")
        else:
            print("ERROR")
    elif result == "1-0":
        print("WHITE")
    elif result == "0-1":
        print("BLACK")
    else:
        print("DEUCE")


    
if LEARN:
    if (os.path.exists(file_name)):
        os.remove(file_name)
    os.mknod(file_name)

    DATAS = prepare_datas(b, care_about_win = True, all_moves = True)
    for i in range(len(DATAS)):
        for j in range(len(DATAS[0])):
            DATAS[i][j] = DATAS[i][j].tolist()
    with open(file_name, 'a+') as jsonfile:
        json.dump(DATAS, jsonfile)
        jsonfile.close()
    
