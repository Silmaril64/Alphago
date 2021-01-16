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

def fileorpackage(name):
    if name.endswith(".py"):
        return name[:-3]
    return name

# *** 11 Layer Encoding ***
# 1  - black stones (1=stone/0=empty)
# 2  - white stones (1=stone/0=empty)
# 3  - current player (1=white/0=black)
# 4  - move t-1 (all zeroes only one cell set to 1)
# 5  - move t-2 (all zeroes only one cell set to 1)
# 6  - move t-3 (all zeroes only one cell set to 1)
# 7  - move t-4 (all zeroes only one cell set to 1)
# 8  - move t-5 (all zeroes only one cell set to 1)
# 9  - move t-6 (all zeroes only one cell set to 1)
# 10 - move t-7 (all zeroes only one cell set to 1)
# 11 - move t-8 (all zeroes only one cell set to 1)
# goal - move t (all zeroes only one cell set to 1, or -1)
def prepare_datas(board, care_about_win = False, all_rotations = True): # all_rotations also say that you only want the board, not the goal
    datas = []
    nb_uses = random.randint(MIN_INFO_FROM_ONE_GAME,MAX_INFO_FROM_ONE_GAME)
    length = len(board._historyMoveNames)
    if (board.result() == "1-0"):
        winner = 1
    elif (board.result() == "0-1"):
        winner = 0
    else:
        winner = 2
    print(winner)
    r = range(length-1)
    moves = board._historyMoveNames
    if all_rotations:
        espe = length / 2. #On ne peut pas prendre le dernier
        ecart = length / 4.
        #Distribution gaussienne pour avoir plus de chances de prendre des données du milieu de partie
        proba_not_normalized = [ (1./(ecart * np.sqrt(2 * np.pi)) * np.exp((i + 1 - espe) ** 2 / (2. * ecart) ** 2))
                           for i in range(length-1)]
        norm = np.linalg.norm(proba_not_normalized)
        proba = [ x / norm for x in proba_not_normalized ]
        chosen_moves = np.random.choice(r, nb_uses,proba)
    else:
        chosen_moves = [length - 1] # Only the last one, because we want a prediction on it
    for i in chosen_moves: #On va s'arrêter au move i, et prédire le suivant
        black = np.zeros((9,9), dtype = int)
        white = np.zeros((9,9), dtype = int)
        memo = [np.zeros((9,9), dtype = int) for z in range(8)]
        
        if (i+1) % 2 == 0: #Le coup actuel (après avoir joué i)
            current = np.ones((9,9), dtype = int)
        else:
            current = np.zeros((9,9), dtype = int)

        if all_rotations:
            goal_move = board.name_to_coord(moves[i+1])
            goal = np.zeros((9,9), dtype = int)
            if care_about_win and ((winner == 1 and current[0][0] != 1) or (winner == 0 and current[0][0] != 0)):
                goal[goal_move[0]][goal_move[1]] = -1
            else:
                goal[goal_move[0]][goal_move[1]] = 1 #Une égalité est traitée comme une victoire (on n'a pas perdu après tout)
        
        for j in range(i+1):
            move = board.name_to_coord(moves[j])
            if j % 2 == 1: # TODO TOFIX black plays first
                black[move[0]][move[1]] = 1
            else:
                white[move[0]][move[1]] = 1
            if (i - j) < 8:
                memo[i - j][move[0]][move[1]] = 1
                
        curr_data = np.dstack((black,white,current, memo[0], memo[1], memo[2], memo[3], memo[4], memo[5], memo[6], memo[7]))


        if all_rotations:
            datas.append([curr_data,  np.reshape(goal, 81)])
            datas.append([np.rot90(curr_data, k=1, axes=(0,1)), np.reshape(np.rot90(goal, k=1, axes=(0,1)), 81)])
            datas.append([np.rot90(curr_data, k=2, axes=(0,1)), np.reshape(np.rot90(goal, k=2, axes=(0,1)), 81)])
            datas.append([np.rot90(curr_data, k=3, axes=(0,1)), np.reshape(np.rot90(goal, k=3, axes=(0,1)), 81)])

            curr_data = np.flipud(curr_data)
            goal = np.flipud(goal)

            datas.append([curr_data, np.reshape(goal, 81)])
            datas.append([np.rot90(curr_data, k=1, axes=(0,1)), np.reshape(np.rot90(goal, k=1, axes=(0,1)), 81)])
            datas.append([np.rot90(curr_data, k=2, axes=(0,1)), np.reshape(np.rot90(goal, k=2, axes=(0,1)), 81)])
            datas.append([np.rot90(curr_data, k=3, axes=(0,1)), np.reshape(np.rot90(goal, k=3, axes=(0,1)), 81)])
        else:
            datas.append([curr_data])
    return datas

print("######################### STARTING GENERATING DATAS #########################")

NB_GAMES = 100 #the number of games played in one epoch
MAX_INFO_FROM_ONE_GAME = 10 #how much info could be used from a single game
MIN_INFO_FROM_ONE_GAME = 5
DATAS = []
VERB = False

file_list = os.listdir('./data/')
nb_files = len(file_list)
print("Actuellement, " + str(nb_files) + " sont présents dans ./data/")
MAX_NB_FILES = 1000

if (nb_files <= MAX_NB_FILES):
    file_name = './data/go_datas_' + str(nb_files + 1) + '.json'
else:
    file_name = './data/go_datas_' + str(random.randint(1, nb_files)) + '.json'
    
if (os.path.exists(file_name)):
    os.remove(file_name)
os.mknod(file_name)

if len(sys.argv) > 2:
    classNames = [fileorpackage(sys.argv[1]), fileorpackage(sys.argv[2])]
elif len(sys.argv) > 1:
    classNames = [fileorpackage(sys.argv[1]), 'myPlayer']
else:
    classNames = ['gnugoPlayer', 'gnugoPlayer']

for i in range(NB_GAMES):
    bad_move = False
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
        
        currentTime = time.time()
        sys.stdout = stringio
        move = players[nextplayer].getPlayerMove() # The move must be given by "A1", ... "J8" string coordinates (not as an internal move)
        sys.stdout = sysstdout
        nbmoves += 1
        otherplayer = (nextplayer + 1) % 2
        othercolor = Goban.Board.flip(nextplayercolor)
        playeroutput = stringio.getvalue()
        stringio.truncate(0)
        stringio.seek(0)
        if VERB:
            print(("[Player "+str(nextplayer) + "] ").join(playeroutput.splitlines(True)))

        outputs[nextplayer] += playeroutput
        totalTime[nextplayer] += time.time() - currentTime
        if VERB:
            print("Player ", nextplayercolor, players[nextplayer].getPlayerName(), "plays: " + move) #changed 
        
        if not Goban.Board.name_to_flat(move) in legals:
            print(otherplayer, nextplayer, nextplayercolor)
            print("Problem: illegal move")
            wrongmovefrom = nextplayercolor
            bad_move = True
            break
        b.push(Goban.Board.name_to_flat(move)) # Here I have to internally flatten the move to be able to check it.
        players[otherplayer].playOpponentMove(move)
 
        nextplayer = otherplayer
        nextplayercolor = othercolor

    for line in os.popen("ps ax | grep gnugo | grep -v grep"):  
        fields = line.split()    
        # extracting Process ID from the output 
        pid = fields[0]  
        # terminating process  
        os.kill(int(pid), signal.SIGKILL)  
    if bad_move:
        continue
    print("The game is over")

    DATAS = prepare_datas(b)
    for i in range(len(DATAS)):
        for j in range(len(DATAS[0])):
            DATAS[i][j] = DATAS[i][j].tolist()
    with open(file_name, 'a+') as jsonfile:
        json.dump(DATAS, jsonfile)
        jsonfile.close()

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

print(DATAS)




