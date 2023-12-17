from base_player import BasePlayer
from random_player import RandomPlayer
from human_player import HumanPlayer
from ai_player import AIPlayer
from hexapp import HexApp

import numpy as np
import pygame

if __name__ == "__main__":
    # First create players with respective strategies
    swap1 = lambda board, *args: BasePlayer.pygame_manual_swap(board, *args)
    swap2 = lambda board, *args: BasePlayer.random_swap(board, *args)

    player1 = AIPlayer()
    player2 = RandomPlayer(swap2)

    # Set up empty board
    dim = 8
    board = np.zeros((dim, dim), dtype=int)

    # Manual changes
    # board[0,0] = 1 # Player 1
    # board[2,2] = 2 # Player 2

    pygame.init()

    play = True
    while play:
        # Game will be completely restarted if play == True
        hex_app = HexApp(board, player1, player2, 1200, 800)
        play = hex_app.execute()

    pygame.quit()
