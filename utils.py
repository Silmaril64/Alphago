import random
import numpy as np


MAX_INFO_FROM_ONE_GAME = 10 #how much info could be used from a single game
MIN_INFO_FROM_ONE_GAME = 5


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
        
        if (i + 1) % 2 == 0: #Le coup actuel (après avoir joué i)
            current = np.ones((9,9), dtype = int) #The whites, because the blacks have just played
        else:
            current = np.zeros((9,9), dtype = int) #The blacks, the first move, (0+1)%2 == 1

        if all_rotations:
            goal_move = board.name_to_coord(moves[i+1])
            goal = np.zeros((9,9), dtype = int)
            if care_about_win and ((winner == 1 and current[0][0] != 1) or (winner == 0 and current[0][0] != 0)):
                goal[goal_move[0]][goal_move[1]] = -1
            else:
                goal[goal_move[0]][goal_move[1]] = 1 #Une égalité est traitée comme une victoire (on n'a pas perdu après tout)
        
        for j in range(i+1):
            move = board.name_to_coord(moves[j])
            print("current move:", move)
            if j % 2 == 0: #black plays first
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
