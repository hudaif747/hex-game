from base_player import BasePlayer
from random_player import RandomPlayer
from human_player import HumanPlayer
# from ai_player_improved import MinMaxPlayer
from ai_player_improved_zobrist_2 import MinMaxPlayer
# from WORKING_FINAL import MinMaxPlayer
from ai_player import AIPlayer
from hexapp import HexApp
from tabulate import tabulate

import numpy as np
import pygame


def colorize(cell):
    # Colorize the cell based on its value
    if cell == "Win":
        return f"\033[92m{cell}\033[0m"  # Green color for Win
    elif cell == "Lose":
        return f"\033[91m{cell}\033[0m"  # Red color for Lose
    else:
        return cell

def print_win_table(totalIterations, player1wins, player2wins, dimension):
    # Initialize data as a list of lists
    data = []
    
    # Fill data with iteration results and colorize cells
    for i in range(totalIterations):
        player1_win_status = colorize("Win" if player1wins[i] == 1 else "Lose")
        player2_win_status = colorize("Win" if player2wins[i] == 1 else "Lose")
        data.append([i + 1, player1_win_status, player2_win_status])

    # Calculate win percentages
    player1_win_percentage = (sum(player1wins) / totalIterations) * 100
    player2_win_percentage = (sum(player2wins) / totalIterations) * 100

    # Add summary data to the end
    data.append(["Summary", f"{player1_win_percentage:.2f}%", f"{player2_win_percentage:.2f}%"])
    
    # Add dimension information
    data.append(["Dimension", dimension])
    
    # Print the table using tabulate
    print(tabulate(data, headers=["Iteration", "Player 1 Win", "Player 2 Win"], tablefmt="grid"))

if __name__ == "__main__":
    # First create players with respective strategies
    swap1 = lambda board, *args: BasePlayer.pygame_manual_swap(board, *args)
    swap2 = lambda board, *args: BasePlayer.random_swap(board, *args)

    dim = 11
    # player1 = MinMaxPlayer(dimension=dim)
    player1 = AIPlayer()
    player2 = RandomPlayer()

    # Set up empty board
    board = np.zeros((dim, dim), dtype=int)

    # Manual changes
    # board[0,0] = 1 # Player 1
    # board[2,2] = 2 # Player 2

    pygame.init()
    
    totalIteration = 10
    currentIteration = 0
    
    player1wins = np.zeros(totalIteration, dtype=int)
    player2wins = np.zeros(totalIteration, dtype=int)

    play = True
    while play:
        # Game will be completely restarted if play == True
        hex_app = HexApp(board, player1, player2, 1200, 800)
        play,fin = hex_app.execute()
        if fin == 1:
            player1wins[currentIteration] = 1
        if fin == 2:
            player2wins[currentIteration] = 1
        currentIteration +=1
        if currentIteration>=totalIteration:
            play = False
        
    print_win_table(totalIteration, player1wins, player2wins, dim)
        
    pygame.quit()