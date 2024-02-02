from base_player import BasePlayer
from hexgame import HexBoard
import numpy as np
import time
import copy

DEPTH = 6

class MinMaxPlayer(BasePlayer):
    def __init__(self, dimension):
        super().__init__()
        self.cache = {}
        self.dimension = dimension
        self.zobrist_keys = self.initialize_zobrist_keys()

    def initialize_zobrist_keys(self):
        dim = (self.dimension, self.dimension)  # Assuming a default size for the Hex board
        num_positions = dim[0] * dim[1]
        num_players = 3  # 0 for empty, 1 for player 1, 2 for player 2
        keys = np.random.randint(2**64, size=(num_positions, num_players), dtype=np.uint64)
        return keys

    def calculate_hash(self, board):
        hash_val = np.uint64(0)  # Ensure the initial value is of type np.uint64
        for i in range(board.dim()[0]):
            for j in range(board.dim()[1]):
                piece = board.get_tile(i, j)
                player_id = np.uint64(0) if piece == 0 else np.uint64(piece)
                position = i * board.dim()[1] + j
                hash_val ^= self.zobrist_keys[position][player_id]
        return hash_val

    def choose_tile(self, board, *args):
        move = self.find_best_move(board, time_limit_seconds=10)
        return move

    def find_best_move(self, board, time_limit_seconds):
        start_time = time.time()
        eval, best_move = self.minimax(board, DEPTH)
        
        # legal_moves = self.get_legal_moves(board)
        # best_move = None
        # best_eval = float('-inf')

        # for move in legal_moves:
        #     clone_board = copy.deepcopy(board)
        #     clone_board.set_tile(*move, 1)
        #     if tuple(clone_board.board.flatten()) in self.cache:
        #         eval = self.cache[tuple(clone_board.board.flatten())]
        #     else:
        #         eval, _ = self.minimax(clone_board, DEPTH)
        #         self.cache[tuple(clone_board.board.flatten())] = eval

        #     if eval > best_eval:
        #         best_eval = eval
        #         best_move = move

        #     elapsed_time = time.time() - start_time
        #     if elapsed_time > time_limit_seconds:
        #         break
        
        return best_move

    def minimax(self, board, depth, alpha=float('-inf'), beta=float('inf'), maximizing_player=True):
        hex_game = HexGameForAI(board)

        if depth == 0 or hex_game.check_finish() != 0:
            return self.evaluate(hex_game.board), None

        legal_moves = self.get_legal_moves(hex_game.board)
        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in legal_moves:
                new_board = HexBoard(hex_game.board.board)
                new_board.set_tile(*move, 1)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in legal_moves:
                new_board = HexBoard(hex_game.board.board)
                new_board.set_tile(*move, 2)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if alpha >= beta:
                    break

            return min_eval, best_move

    def get_legal_moves(self, board):
        valid_moves = [(i, j) for i in range(board.dim()[1]) for j in range(board.dim()[0]) if board.get_tile(i, j) == 0]
        return valid_moves

    def evaluate(self, board):
        hash_val = self.calculate_hash(board)

        if hash_val in self.cache:
            return self.cache[hash_val]

        player1_connected = self.check_player_connected(board, 1)
        player2_connected = self.check_player_connected(board, 2)

        if player1_connected:
            evaluation_value = 1000  # Player 1 wins
        elif player2_connected:
            evaluation_value = -1000  # Player 2 wins
        else:
            # Evaluate based on the number of connected components for each player
            player1_components = self.count_connected_components(board, 1)
            player2_components = self.count_connected_components(board, 2)
            evaluation_value = player1_components - player2_components

        self.cache[hash_val] = evaluation_value
        return evaluation_value

    def check_player_connected(self, board, player_id):
        if player_id == 1:
            # Check if player 1 is connected from top to bottom
            for j in range(board.dim()[1]):
                if self.dfs(board, 0, j, player_id, set()):
                    return True
        elif player_id == 2:
            # Check if player 2 is connected from left to right
            for i in range(board.dim()[0]):
                if self.dfs(board, i, 0, player_id, set()):
                    return True
        return False

    def dfs(self, board, i, j, player_id, visited):
        if not (0 <= i < board.dim()[0]) or not (0 <= j < board.dim()[1]) or board.get_tile(i, j) != player_id:
            return False

        if (i, j) in visited:
            return False

        visited.add((i, j))

        if player_id == 1 and i == board.dim()[0] - 1:
            return True
        elif player_id == 2 and j == board.dim()[1] - 1:
            return True

        neighbors = [(i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1), (i + 1, j), (i + 1, j - 1)]

        for neighbor in neighbors:
            if self.dfs(board, neighbor[0], neighbor[1], player_id, visited):
                return True

        return False

    def count_connected_components(self, board, player_id):
        visited = set()
        components = 0

        for i in range(board.dim()[0]):
            for j in range(board.dim()[1]):
                if board.get_tile(i, j) == player_id and (i, j) not in visited:
                    components += 1
                    self.dfs(board, i, j, player_id, visited)

        return components
    
    def get_whether_terminated(self,board):
        game = HexGameForAI(board)
        return game.check_finish()
       
class HexGameForAI:
    def __init__(self, board):
        self.board = HexBoard(board.board)
        
    def check_finish(self) -> int:
        # We build a "visited" matrix for both players, similar to bfs/dfs
        visited = np.zeros(self.board.dim(), dtype=int)

        # Check player 1 (red, top)
        pl_id = 1
        for j in range(visited.shape[1]):
            if self.board.get_tile(0, j) == pl_id:
                visited[0, j] = pl_id
                visited = self.__visit(0, j, pl_id, visited)

        if np.any(visited[-1, :] == pl_id):
            return pl_id

        # Check player 2 (blue, left)
        pl_id = 2
        for i in range(visited.shape[0]):
            if self.board.get_tile(i, 0) == pl_id:
                visited[i, 0] = pl_id
                self.__visit (i, 0, pl_id, visited)

        if np.any(visited[:, -1] == pl_id):
            return pl_id

        return 0  # game goes on
    
    def __visit(self, i, j, player, visited) -> np.ndarray:
        x_dim, y_dim = self.board.dim()
        candidates = [(i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1), (i + 1, j), (i + 1, j - 1)]
        neighbors = [(i, j) for (i, j) in candidates if 0 <= i < y_dim and 0 <= j < x_dim]

        for (k, l) in neighbors:
            if self.board.get_tile(k, l) == player and not visited[k, l]:
                visited[k, l] = player
                visited = self.__visit(k, l, player, visited)
        return visited
