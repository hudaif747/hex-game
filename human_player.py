from base_player import BasePlayer


class HumanPlayer(BasePlayer):
    def choose_tile(self, board, *args) -> tuple:
        """
        Chooses a tile based on given heuristic / algorithm.

        Parameters
        ----------
        board : HexBoard
            Current state of the Hex board.
        args : tuple, optional
            Further parameters in tuple possibly required by heuristic.

        Returns
        -------
        res : tuple (int, int)
            Indices of resulting tile.

        """
        return args[0], args[1]
    
    def get_whether_terminated(self,board):
        return 0