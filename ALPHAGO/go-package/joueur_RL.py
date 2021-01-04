"""# -*- coding: utf-8 -*-
''' This is the famous random player whici (almost) always looses.
'''

import time
import Goban 
from random import choice
from playerInterface import *
import numpy as np
from tensorflow import keras

MODEL_PATH = "model.pb"
model = keras.models.load_model('model.pb')




class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self, i_model = None):
        self._board = Goban.Board()
        self._mycolor = None
        if (i_model == None):
            self._model = model
        else:
            self._model = i_model

    def getPlayerName(self):
        return "RL Player"

    def encode(self):
        

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        proba = np.zeros((9,9), dtype = np.float)
        for m in moves:
            self._board.push(m)
            model
            
        move = choice(moves)
        self._list_of_moves.append(move)
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move, "i.e. ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._list_of_moves.append(move)
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")
"""

from multiprocessing import Pool
from playerInterface import *
from Goban import Board
import random
import math
import copy
import time
import Goban 
import numpy as np
from tensorflow import keras

MODEL_PATH = "model.pb"
MODEL_VALUE = 10 # A constant to calculate the mean in UTC 
model = keras.models.load_model('.')

class myPlayer(PlayerInterface):

    def __init__(self, i_model = None):
        self._board = Board()
        self._mycolor = None
        if (i_model == None):
            self._model = model
        else:
            self._model = i_model
        

    def getPlayerName(self):
        return "RL player"

    def encode(self, board):
        toPush = _historyMoveNames
        black_stones = np.zeros((9,9), dtype=np.float32)
        white_stones = np.zeros((9,9), dtype=np.float32)
        if (len(data[i]["list_of_moves"])%2 == 0): # I respect the model convention
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
        return(np.dstack((black_stones,white_stones,player_turn)))
            
            
    
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

    @staticmethod
    def select_move(board_org, max_time=7.4, temperature=1.2):
        start_time = time.time()
        root = MCTSNode(board_org.weak_legal_moves())
        # add nodes (at least 10,000 rollouts per turn)
        i=0
        pool = Pool()
        while(True):
            board = copy.deepcopy(board_org)
            node = root
            while (not node.can_add_child()) and (not board.is_game_over()):
                node = myPlayer.select_child(node, board, temperature)
                #board.push(node.move)
            if node.can_add_child() and not board.is_game_over():
                node = node.add_random_child(board)
                #board.push(node.move)
            winners = []
            results = []
            # use all cores of the processor
            for proc in range(pool._processes):
                results.append(pool.apply_async(myPlayer.simulate_random_game, [board]))
            for res in results:
                winners.append(res.get())
            while node is not None:
                for winner in winners:
                    node.record_win(winner)
                node = node.parent
            if (time.time() - start_time >= max_time):
                print()
                break
            i+=pool._processes
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
        return best_move

    @staticmethod
    def select_child(node, board, temperature):
        # upper confidence bound for trees (UCT) metric
        total_rollouts = sum(child.num_rollouts for child in node.children)
        log_rollouts = math.log(total_rollouts)

        best_score = -1
        best_child = None
        # loop over each child.
        tempo_board = encode(board) # We will have to push the current move in it
        for child in node.children:
            # calculate the UCT score.
            win_percentage = child.winning_frac(board.next_player(), encoding) # MODIFIER CETTE LIGNE 
            exploration_factor = math.sqrt(log_rollouts / child.num_rollouts)
            uct_score = win_percentage + temperature * exploration_factor
            # Check if this is the largest we've seen so far.
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        board.play_move(best_child.move)
        return best_child

    @staticmethod
    def simulate_random_game(board):
        def is_point_an_eye(board, coord):
            # We must control 3 out of 4 corners if the point is in the middle
            # of the board; on the edge we must control all corners.
            friendly_corners = 0
            off_board_corners = 0
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

    def winning_frac(self, player, encoding):
        tempo_move = flat_to_coord(self.move)
        encoding[tempo_move[0]][tempo_move[1]][not player] = 1
        proba = model.predict([encoding])
        encoding[tempo_move[0]][tempo_move[1]][not player] = 0
        return float(self.win_counts[player] + proba * MODEL_VALUE) / float(self.num_rollouts + MODEL_VALUE)
