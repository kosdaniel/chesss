"""
Module for human player classes
"""

import pygame as pg
from app.src.player import player
from app.src.engine import chessboard
from app.src.gui import inputhandler
from app.src.gui import boardview

class LocalHumanPlayer(player.Player):
    """
    Local human player class
    """
    def __init__(self, color: int, chessboard: chessboard.Chessboard, board_view: boardview.BoardView):
        super().__init__(color, chessboard)
        self.board_view = board_view
        self.input_handler = inputhandler.InputHandler(self.chessboard, self.board_view)
        self.moves = []

    def get_move(self):
        """
        Returns a move if player has created a move, else None
        """
        if self.moves == []:
            return None
        res = self.moves[0]
        self.moves = self.moves[1:]
        return res
    
    def handle_input(self, event: pg.event.Event, disable_input: bool = False):
        """
        Calls handle input from input handler and stores the resulting move if one has been created
        """
        move = self.input_handler.handle_input(event, disable_input)
        if move is not None:
            self.moves.append(move)


class RemoteHumanPlayer(player.Player):
    """
    Remote human player class
    """
    def __init__(self, color: int, chessboard: chessboard.Chessboard, network_interface):
        super().__init__(color, chessboard)
        self.network_interface = network_interface

    def get_move(self):
        """
        todo
        """
        return self.network_interface.poll_for_move()