"""
Module for the computer player class
"""

from app.src.player import player
from app.src.engine import chessboard, ai
from app import config as cf


class ComputerPlayer(player.Player):
    """
    Computer player class
    """
    def __init__(self, color: int, chessboard: chessboard.Chessboard):
        super().__init__(color, chessboard)
        self.ai = ai.AI()

    def get_move(self):
        """
        Polls the member AI object for a move, returns it if there is one else returns None
        """
        return self.ai.poll_for_move(self.chessboard)
    
    def stop_calculating(self):
        """
        Disallows AI object to calculate moves
        """
        self.ai.quit()
        



