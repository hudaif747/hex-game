import numpy as np
from collections import deque
from base_player import BasePlayer

class AIPlayer(BasePlayer):
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
        return self.enhanced_heuristic(board)

    def enhanced_heuristic(self, board) -> tuple:
        """
        Enhanced heuristic for AI move.

        Parameters
        ----------
        board : HexBoard
            Current state of the Hex board.

        Returns
        -------
        res : tuple (int, int)
            Indices of the resulting tile.

        """
        valid_moves = [(i, j) for i in range(board.dim()[1]) for j in range(board.dim()[0]) if board.get_tile(i, j) == 0]
        scores = []

        for move in valid_moves:
            score = self.evaluate_move(board, move)
            scores.append((move, score))

        # Sort moves by their scores in descending order
        sorted_moves = sorted(scores, key=lambda x: x[1], reverse=True)

        # Select the move with the highest score
        chosen_move = sorted_moves[0][0]

        return chosen_move

    def evaluate_move(self, board, move) -> float:
        """
        Evaluates a move using an enhanced heuristic.

        Parameters
        ----------
        board : HexBoard
            Current state of the Hex board.
        move : tuple (int, int)
            Indices of the move to evaluate.

        Returns
        -------
        value : float
            Score of the move.

        """
        opponent_id = 3 - self.id  # Assuming player ids are 1 and 2
        # Calculate the distance to the opponent's sides
        distance_to_opponent_sides = self.distance_to_opponent_sides(board, move, opponent_id)
        # Calculate the distance to the closest opponent tile
        min_distance_to_opponent = self.min_distance_to_opponent(board, move, opponent_id)
        # Combine these factors to get a score
        score = 1 / (1 + min_distance_to_opponent) + 1 / (1 + distance_to_opponent_sides)

        return score

    def min_distance_to_opponent(self, board, move, opponent_id) -> float:
        queue = deque([(move, 0)])
        visited = set()

        while queue:
            current_pos, distance = queue.popleft()
            i, j = current_pos

            # Check if the current position is an opponent tile
            if board.get_tile(i, j) == opponent_id:
                return distance

             # Add neighboring positions to the queue if not visited
            neighbors = board.get_neighbors(i, j)

            # Sort neighbors to prioritize downward direction
            neighbors.sort(key=lambda x: x[0], reverse=True)

            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))
                    visited.add(neighbor)

        return float('inf')
  
    def distance_to_opponent_sides(self, board, move, opponent_id) -> float:
        queue = deque([(move, 0)])
        visited = set()

        while queue:
            current_pos, distance = queue.popleft()
            i, j = current_pos

            # Check if the current position is on the opponent's side
            if self.is_on_opponent_side(board, i, j, opponent_id):
                return distance

            # Add neighboring positions to the queue if not visited
            neighbors = board.get_neighbors(i, j)
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))
                    visited.add(neighbor)


        return float('inf')  # Not on the opponent's side
    
    def is_on_opponent_side(self, board, i, j, opponent_id) -> bool:
        """
        Checks if the given position is on the opponent's side.

        Parameters
        ----------
        board : HexBoard
            Current state of the Hex board.
        i : int
            Row index of the position.
        j : int
            Column index of the position.
        opponent_id : int
            ID of the opponent player.

        Returns
        -------
        on_opponent_side : bool
            True if the position is on the opponent's side, False otherwise.

        """
       # For player 1 (ID 1), check if the position is on the left side
        if opponent_id == 1 and j == 0:
            return True

        # For player 2 (ID 2), check if the position is on the top side
        if opponent_id == 2 and i == 0:
            return True

        return False