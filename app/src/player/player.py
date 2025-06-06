"""
Module for an abstract player class
"""
from app.src.engine import chessboard
from abc import ABC, abstractmethod

class Player(ABC):
    """
    abstract class player
    """
    def __init__(self, color: int, chessboard: chessboard.Chessboard):
        self.color = color
        self.chessboard = chessboard

    @abstractmethod
    def get_move(self):
        """
        Returns a Move from the player if he has created a move, else None
        """
        pass