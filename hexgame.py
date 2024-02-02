import numpy as np

class HexBoard:
    def __init__(self, board):
        """
    Save initial board provided by user.

    If an entry equals zero, then it can be chosen by a player, otherwise
    the value corresponds to the respective player (1 or 2).

    Parameters
    ----------
    board : numpy array
        Matrix representation of board.
    
    """
        self.board = board.astype(int)

    def dim(self) -> tuple:
        # Returns dimension of board (x-direction, y-direction)
        return self.board.shape[1], self.board.shape[0]

    def swap(self) -> None:
        # Performs a swap in Hex game by swapping colors and mirroring the board.
        ones = (self.board == 1)
        twos = (self.board == 2)
        self.board[ones], self.board[twos] = 2, 1
        self.board = self.board.transpose()

    def get_tile(self, i, j) -> int:
        # Returns value of tile (i,j)
        return self.board[i, j]

    def set_tile(self, i, j, val) -> bool:
        # Sets value of tile (i,j).
        # Returns true if tile was not already occupied, otherwise returns False.

        # Check if tile indices are valid (not out of bounds)
        if i < 0 or j < 0 or i >= self.board.shape[1] or j >= self.board.shape[0]:
            return False

        # Check if tile can be set
        if self.board[i, j] == 0:
            self.board[i, j] = val
            return True
        return False

    def get_row(self, i):
        # Returns ith row of the board if i is valid index, otherwise None.
        if 0 <= i < self.board.shape[1]:
            return self.board[i, :]
        return None

    def get_col(self, j):
        # Returns jth column of the board if i is valid index, otherwise None.
        if 0 <= j < self.board.shape[0]:
            return self.board[:, j]
        return None
    def get_neighbors(self, i, j):
        """
        Get neighboring positions of a given position (i, j) on the Hex board.

        Parameters
        ----------
        i : int
            Row index of the position.
        j : int
            Column index of the position.

        Returns
        -------
        neighbors : list of tuples
            List of neighboring positions.
        """
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, -1)]

        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.board.shape[0] and 0 <= nj < self.board.shape[1]:
                neighbors.append((ni, nj))
        
        return neighbors

    def __str__(self) -> str:
        return self.board.__str__()

    def __repr__(self) -> str:
        return self.board.__repr__()


class HexGame:
    def __init__(self, board, player1, player2):
        """
    Initializes hex game.

    Parameters
    ----------
    board : numpy array
        Matrix representation of board. Dimension will be deduced from this matrix.
    player1 : Player
        Instance of class Player representing player 1 (red player).
    player2 : Player
        Instance of class Player representing player 2 (blue player).
    """
        # Initialize board
        self.board = HexBoard(board)
        self.players = [player1, player2]

        player1.set_id(1)
        player2.set_id(2)

        self._num_players = 2
        self._current_player = 1

        self._turns = 1

    def wait_for_swap(self) -> bool:
        return self._turns == 2

    def switch_player(self):
        self._current_player = (self._current_player % self._num_players) + 1

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
                self.__visit(i, 0, pl_id, visited)

        if np.any(visited[:, -1] == pl_id):
            return pl_id

        return 0  # game goes on

    def turn(self, *args):
        # Player gets new tile if it does not already belong to opposite player

        (i, j) = self.players[self._current_player - 1].choose_tile(self.board, *args)
        valid = self.board.set_tile(i, j, self._current_player)
        if valid:
            self._turns += 1
            self.switch_player()

        return valid

    def get_player(self):
        return self._current_player

    def get_turn(self):
        return self._turns

    def set_turn(self, turn):
        self._turns = turn

    def swap(self, *args):
        # TODO: Check if also IDs have to be swapped.
        if self.wait_for_swap():
            res = self.players[self._current_player - 1].claim_swap(self.board, *args)
            if res:
                self.board.swap()
                self.switch_player()
                self.players[0].id, self.players[1].id = self.players[1].id, self.players[0].id

    # "Private" methods
    def __visit(self, i, j, player, visited) -> np.ndarray:
        x_dim, y_dim = self.board.dim()
        candidates = [(i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1), (i + 1, j), (i + 1, j - 1)]
        neighbors = [(i, j) for (i, j) in candidates if 0 <= i < y_dim and 0 <= j < x_dim]

        for (k, l) in neighbors:
            if self.board.get_tile(k, l) == player and not visited[k, l]:
                visited[k, l] = player
                visited = self.__visit(k, l, player, visited)
        return visited


class PuzzleHexGame(HexGame):
    def check_finish(self):
        return self.players[1].get_whether_terminated(self.board)

    def get_winner(self) -> int:
        return self.players[0].get_id() if self.players[0].get_whether_terminated(self.board) else 0