from base_player import BasePlayer
from hexgame import HexGame
from hexgame import HexBoard
import numpy as np
import heapq
import time
import copy

DEPTH = 3

class MinMaxPlayer(BasePlayer):
    def __init__(self):
        super().__init__()
        self.cache = {}  # Dictionary to store cached evaluations
        
    def choose_tile(self, board, *args) -> tuple:
        """
        Chooses a tile based on the AI's strategy.

        Parameters
        ----------
        board : HexBoard
            Current state of the Hex board.
        args : tuple, optional
            Further parameters possibly required by the AI strategy.

        Returns
        -------
        res : tuple (int, int)
            Indices of the resulting tile.

        """
        print("======================================")
        print(board)
        print("======================================")
        move = self.find_best_move(board,30) #time constraint
        return move

    
    def find_best_move(self, board, time_limit_seconds):
        start_time = time.time()

        # legal_moves = self.get_legal_moves(board)
        # best_move = None
        eval, best_move = self.minimax(board, DEPTH)
        # best_eval = float('-inf')

        # for move in legal_moves:
        #     clone_board = copy.deepcopy(board)
        #     clone_board.set_tile(*move, self.id)
        #     if tuple(clone_board.board.flatten()) in self.cache:
        #         eval = self.cache[tuple(clone_board.board.flatten())]
        #     else:
        #         eval, _ = self.minimax(clone_board, DEPTH)
        #         # Cache the evaluation result
        #         self.cache[tuple(clone_board.board.flatten())] = eval


        #     if eval > best_eval:
        #         print("*********************************************")
        #         print(clone_board)
        #         print("*********************************************")
        #         print("best eval: ",best_eval)
        #         print("best move: ",best_move)
        #         best_eval = eval
        #         best_move = move

        #     elapsed_time = time.time() - start_time
        #     if elapsed_time > time_limit_seconds:
        #         break
        # print("*********************************************")
        # print("selected best move: ",best_move)        
        # print("*********************************************")
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
                new_board.set_tile(*move, self.id)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if alpha >= beta:  # Corrected condition
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in legal_moves:
                # new_board = HexBoard(board.board) 
                new_board = HexBoard(hex_game.board.board) 
                new_board.set_tile(*move, 3 - self.id)  # Assume 3 - self.id is the opponent's id
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if alpha >= beta:  # Corrected condition
                    break
                
            return min_eval, best_move
        
    def get_legal_moves(self, board):
        valid_moves = []
        valid_moves = [(i, j) for i in range(board.dim()[1]) for j in range(board.dim()[0]) if board.get_tile(i, j) == 0]
        # print(valid_moves)
        # print(board)
        return valid_moves

    def evaluate(self, board) -> float:
        player1_shortest_path = self.get_shortest_path(board, 1)
        player2_shortest_path = self.get_shortest_path(board, 2)

        own_path = player1_shortest_path if self.id == 1 else player2_shortest_path
        opponent_path = player2_shortest_path if self.id == 1 else player1_shortest_path
        
        path_difference = len(own_path) - len(opponent_path)

        # Penalize the longer opponent path
        penalty_factor = 0.1  # Adjust this factor based on your preferences
        path_score = path_difference - penalty_factor * len(opponent_path)

        # Bonus for each tile placed on the player's own path
        own_path_bonus = 0.5  # Adjust this factor based on your preferences
        for move in self.get_legal_moves(board):
            if move in own_path:
                path_score += own_path_bonus
        
        return path_score

    def get_shortest_path(self, board, player_id):
        graph = Graph(board.board, player_id)
        return graph.get_shortest_path()
    
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

class Graph:
    def __init__(self, board, player_id):
        self.board = HexBoard(board)
        self.player_id = player_id

    def get_shortest_path(self):
        start_positions = self.get_start_positions()
        shortest_paths = []
        for start_position in start_positions:
            path = self.dijkstra(start_position)
            shortest_paths.append(path)
        return min(shortest_paths, key=len)

    def get_start_positions(self):
        if self.player_id == 1:
            return [(0, j) for j in range(self.board.dim()[1])]
        elif self.player_id == 2:
            return [(i, 0) for i in range(self.board.dim()[0])]

    def dijkstra(self, start_position):
        x_dim, y_dim = self.board.dim()
        heap = [(0, start_position)]
        visited = set()

        while heap:
            current_distance, current_position = heapq.heappop(heap)
            if current_position in visited:
                continue

            visited.add(current_position)

            if self.player_id == 1 and current_position[0] == y_dim - 1:
                return visited  # Player 1 connects top to bottom
            elif self.player_id == 2 and current_position[1] == x_dim - 1:
                return visited  # Player 2 connects left to right

            neighbors = self.get_neighbors(current_position)
            for neighbor in neighbors:
                if neighbor not in visited:
                    distance_to_neighbor = 1  # Assuming uniform edge weights
                    heapq.heappush(heap, (current_distance + distance_to_neighbor, neighbor))

    def get_neighbors(self, position):
        i, j = position
        candidates = [(i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1), (i + 1, j), (i + 1, j - 1)]
        return [(i, j) for (i, j) in candidates if 0 <= i < self.board.dim()[0] and 0 <= j < self.board.dim()[1]] 