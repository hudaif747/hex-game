from base_player import BasePlayer
import numpy as np

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
        return self.improved_heuristic(board)

    def improved_heuristic(self, board) -> tuple:
        """
        Improved heuristic for AI move.

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
        Evaluates a move using an improved heuristic.

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

        # Calculate the distance to the closest opponent tile
        min_distance_to_opponent = self.min_distance_to_opponent(board, move, opponent_id)

        # Calculate the distance to the center of the board
        distance_to_center = self.distance_to_center(board, move)

        # Calculate the number of neighboring tiles controlled by the AI player
        ai_controlled_neighbors = self.count_ai_controlled_neighbors(board, move)

        # Introduce some randomness to avoid purely horizontal and vertical moves
        randomness = np.random.uniform(0.8, 1.2)

        # Combine these factors to get a score
        score = (
            1 / (1 + min_distance_to_opponent) +
            0.2 / (1 + distance_to_center) * randomness +
            0.5 * ai_controlled_neighbors
        )
        
        return score

    def min_distance_to_opponent(self, board, move, opponent_id) -> float:
        distances = []

        for i in range(board.dim()[1]):
            for j in range(board.dim()[0]):
                if board.get_tile(i, j) == opponent_id:
                    distance = np.sqrt((i - move[0]) ** 2 + (j - move[1]) ** 2)
                    distances.append(distance)

        if distances:
            return min(distances)
        else:
            return float('inf')

    def distance_to_center(self, board, move) -> float:
        """
        Calculates the distance from the chosen move to the center of the board.

        Parameters
        ----------
        board : HexBoard
            Current state of the Hex board.
        move : tuple (int, int)
            Indices of the chosen move.

        Returns
        -------
        distance : float
            Distance from the move to the center of the board.

        """
        center_row = board.dim()[1] // 2
        center_col = board.dim()[0] // 2

        i, j = move
        distance = np.sqrt((i - center_row) ** 2 + (j - center_col) ** 2)

        return distance

    def count_ai_controlled_neighbors(self, board, move) -> int:
        """
        Counts the number of neighboring tiles controlled by the AI player.

        Parameters
        ----------
        board : HexBoard
            Current state of the Hex board.
        move : tuple (int, int)
            Indices of the chosen move.

        Returns
        -------
        count : int
            Number of neighboring tiles controlled by the AI player.

        """
        i, j = move
        neighbors = board.get_neighbors(i, j)

        count = sum(board.get_tile(*neighbor) == self.id for neighbor in neighbors)

        return count
