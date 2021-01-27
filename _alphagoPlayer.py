"""# -*- coding: utf-8 -*-
''' This is the famous random player which (almost) always looses.
"""

from playerInterface import *
from Goban import Board
import random
import math
import copy
import time
import Goban 
import numpy as np
from tensorflow import keras
from utils import prepare_datas

STRONG_BASE_MODEL_PATH = "./models/strongPolicyNetwork"
#STRONG_BASE_MODEL_PATH = "./models/fastPolicyNetwork"
FAST_BASE_MODEL_PATH = "./models/fastPolicyNetwork"
#MODEL_VALUE = 10 # A constant to calculate the mean in UTC # Selon Mr Simon, une moyenne non pondérée suffit
s_base_model = keras.models.load_model(STRONG_BASE_MODEL_PATH)
f_base_model = keras.models.load_model(FAST_BASE_MODEL_PATH) #The base model to be used if nothing is given at the initialization

class myPlayer(PlayerInterface):

    def __init__(self, s_model = None, f_model = None):
        self._board = Board()
        self._mycolor = None
        if (s_model == None):
            self._strong_model = s_base_model
        else:
            self._strong_model = s_model

        if (f_model == None):
            self._fast_model = f_base_model
        else:
            self._fast_model = f_model
        

    def getPlayerName(self):
        return "RL player"

    def encode(self, board):
        toPush = board._historyMoveNames
        lenToPush = len(toPush)
        black_stones = np.zeros((9,9), dtype=np.float32)
        white_stones = np.zeros((9,9), dtype=np.float32)
        memo = [np.zeros((9,9), dtype = int) for z in range(8)]
        if (lenToPush%2 == 0): # I respect the model convention / if (len(data[i]["list_of_moves"])%2 == 0):
            player_turn = np.ones((9,9), dtype=np.float32)
        else:
            player_turn = np.zeros((9,9), dtype=np.float32)
        toPlay = 0
        for move in toPush:
            move = name_to_coord(move)
            if (toPlay): # 1 is white
                white_stones[move[0],move[1]] = 1
            else:
                black_stones[move[0],move[1]] = 1
            toPlay = (toPlay + 1) % 2
        for i in range(8):
            if lenToPush >= i:
                move_history = name_to_coord(toPush[-i])
                memo[8-i,move[0],move[1]] = 1
        return(np.dstack((black_stones,white_stones,player_turn, memo[0], memo[1], memo[2], memo[3], memo[4], memo[5], memo[6], memo[7])))
            
            
    
    def getPlayerMove(self):
        if self._board.is_game_over():
            return "PASS"
        move = self.select_move(self._board)
        self._board.play_move(move)
        return Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        self._board.play_move(Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won :D")
        else:
            print("I lost :(")

    def select_move(self, board_org, max_time=7.4, temperature=1.2):
        start_time = time.time()
        root = MCTSNode(board_org.weak_legal_moves())
        # add nodes (at least 10,000 rollouts per turn)
        i=0
        while(True):
            board = copy.deepcopy(board_org)
            node = root
            while (not node.can_add_child()) and (not board.is_game_over()):
                node = self.select_child(node, board, temperature)
                #board.push(node.move)
            if node.can_add_child() and not board.is_game_over():
                node = node.add_random_child(board)
                #board.push(node.move)
            winner = self.simulate_random_game(board)
            while node is not None:
                node.record_win(winner)
                node = node.parent
            if (time.time() - start_time >= max_time):
                print()
                break
            i+=1
            print("Rounds %d (%f)" % (i,time.time()-start_time), end='\r')
        # debug
        scored_moves = [(child.winning_frac(board_org.next_player()), child.move, child.num_rollouts)
                        for child in root.children]
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        for s, m, n in scored_moves[:5]:
            print('%s - %.3f (%d)' % (m, s, n))
        # pick best node
        best_move = -1
        best_pct = -1.0
        for child in root.children:
            child_pct = child.winning_frac(board_org.next_player())
            if child_pct > best_pct:
                best_pct = child_pct
                best_move = child.move
        print('Select move %s with win pct %.3f' % (best_move, best_pct))
        # TODO: Here, get the best root children  
        return best_move

    def select_child(self, node, board, temperature):
        # upper confidence bound for trees (UCT) metric
        total_rollouts = sum(child.num_rollouts for child in node.children)
        log_rollouts = math.log(total_rollouts)

        best_score = -1
        best_child = None
        # loop over each child.
        #tempo_board = encode(board) # We will have to push the current move in it
        data_prepared = np.array([prepare_datas(board, all_rotations = False)[0][0]], dtype = int)
        #print(data_prepared, len(data_prepared), len(data_prepared[0]), len(data_prepared[0][0]),  flush = True)
        policy_prediction = self._strong_model.predict( data_prepared ) # TODO: Verify if everything's okay with this line
        for child in node.children:
            # calculate the UCT score.
            win_percentage = (policy_prediction[0][child.move] + child.winning_frac(board.next_player())) / 2.0 # TODO: Verifier que name_to_flat donne bien la bonne case
            exploration_factor = math.sqrt(log_rollouts / child.num_rollouts)
            uct_score = win_percentage + temperature * exploration_factor
            # Check if this is the largest we've seen so far.
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        board.play_move(best_child.move)
        return best_child

    def simulate_random_game(self, board):
        def is_point_an_eye(board, coord):
            # We must control 3 out of 4 corners if the point is in the middle
            # of the board; on the edge we must control all corners.
            friendly_corners = 0
            i_org = i = board._neighborsEntries[coord]
            while board._neighbors[i] != -1:
                n = board._board[board._neighbors[i]]
                if  n == board.next_player():
                    return False
                if (n != Board._EMPTY) or (n != board.next_player()):
                    friendly_corners += 1
                i += 1
            if i >= i_org+4:
                # Point is in the middle.
                return friendly_corners >= 3
            # Point is on the edge or corner.
            return (4-i_org-i) + friendly_corners == 4
        # ==============================
        while not board.is_game_over():
            moves = board.weak_legal_moves()
            random.shuffle(moves)
            valid_move = -1 # PASS
            for move in moves:
                if not(is_point_an_eye(board, move)) and (board.play_move(move)):
                    valid_move = move
                    break
            if valid_move == -1:
                board.play_move(-1)
        # TODO convert this random rollout using the following algo :
        #while not board.is_game_over():
        #    move_probabilities = self._fast_policy.predict(board)
        #    greedy_move = max(move_probabilities)
        #    board.play_move(greedy_move)
        if (board._nbWHITE > board._nbBLACK):
            return "1-0"
        elif (board._nbWHITE < board._nbBLACK):
            return "0-1"
        else:
            return "1/2-1/2"
        #return board.result()



class MCTSNode():

    def __init__(self, unvisited_moves, parent=None, move=None):
        self.parent = parent
        self.move = move
        self.win_counts = {
            Board._BLACK: 0,
            Board._WHITE: 0,
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = unvisited_moves
        random.shuffle(self.unvisited_moves)

    def add_random_child(self, board):
        new_move = self.unvisited_moves.pop()
        while (new_move == -1) and (board.play_move(new_move) == False):
            if not self.can_add_child():
                return self
            new_move = self.unvisited_moves.pop()
        new_node = MCTSNode(board.weak_legal_moves(), self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner):
        if winner == "1-0": 
            self.win_counts[Board._WHITE] += 1
        elif winner == "0-1":
            self.win_counts[Board._BLACK] += 1
        self.num_rollouts += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self, board):
        return board.is_game_over()

    def winning_frac(self, player):
        #tempo_move = flat_to_coord(self.move)
        #encoding[tempo_move[0]][tempo_move[1]][not player] = 1
        #proba = model.predict([encoding])
        #encoding[tempo_move[0]][tempo_move[1]][not player] = 0
        return float(self.win_counts[player]) / float(self.num_rollouts)
        #return float(self.win_counts[player] + proba * MODEL_VALUE) / float(self.num_rollouts + MODEL_VALUE)
