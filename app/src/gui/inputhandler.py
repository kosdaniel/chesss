"""
Module implementing the input handler class
"""

import pygame as pg
from app.src.engine import chessboard
from app.src.gui import boardview
from app.src.engine import game_logic as gl
import numpy as np


class InputHandler():
    """
    Class used to handle mouse input from the player. It is used simultaneously for rendering and move creation purposes as 
    they are intertwined. It uses a finite state machine to represent all possible stages of move creation
    """
    no_piece_selected = 10
    piece_selected = 11
    piece_selected_and_dragging = 12
    awaiting_promotion_choice = 13

    def __init__(self, chessboard: chessboard.Chessboard, board_view: boardview.BoardView):
        """
        Initialize the input handler object with a chessboard and board view object. 
        Board view object is used to get the correct chess square indices based on the provided mouse coordinates
        """
        self.chessboard = chessboard
        self.board_view = board_view
        self.clear()

    def clear(self):
        """
        Set the FSM to the initial state
        """
        self.selected_src = None
        self.legal_moves = np.uint64(0)
        self.drag = False
        self.promotion_square = None
        self.state = self.no_piece_selected
        self.selected_twice = False
        self.mouse_x = None
        self.mouse_y = None
        

    def get_state(self):
        """
        Return all information of the current state of the input handler related to rendering. Used by board view
        """
        return self.selected_src, self.legal_moves, self.drag, self.promotion_square, self.mouse_x, self.mouse_y
     

    def handle_input(self, event: pg.event.Event, disable_input: bool = False) -> gl.Move | None:
        """
        Method used for handling a single mouse input event. It is expected to be called for every mouse event
        currently present in the event queue, every frame. The method returns a move if the FSM reaches a point where
        a legal move was created and clears the FSM, otherwise it returns None
        The disable input arg is used to disallow move creation when waiting for a move from a different source
        but still allow piece clicking, dragging, highlighting etc.
        """
        match self.state:
            case self.no_piece_selected:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse_x, self.mouse_y = event.pos
                    pos = self.board_view.get_pos(self.mouse_x, self.mouse_y)
                    if pos & self.chessboard.board_state.occupied() != 0:
                        self.selected_src = pos
                        self.state = self.piece_selected_and_dragging
                        self.drag = True
                        if not disable_input:
                            self.legal_moves = self.chessboard.get_legal_moves(pos, True)
                    else:
                        self.clear()
                return None
            case self.piece_selected:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse_x, self.mouse_y = event.pos
                    pos = self.board_view.get_pos(self.mouse_x, self.mouse_y)
                    if self.legal_moves & pos != 0:
                        if self.chessboard.is_promotion(self.selected_src, pos):
                            self.promotion_square = pos
                            self.state = self.awaiting_promotion_choice
                            self.drag = False
                            return None
                        piece_type = self.chessboard.get_piece_at_pos(self.selected_src)
                        res = gl.Move(self.selected_src, pos, piece_type[1], piece_type[0])
                        self.clear()
                        return res
                    if pos & self.chessboard.board_state.occupied() != 0:
                        if pos & self.selected_src != 0:
                            self.selected_twice = True
                        self.selected_src = pos
                        self.state = self.piece_selected_and_dragging
                        self.drag = True
                        if not disable_input:
                            self.legal_moves = self.chessboard.get_legal_moves(pos, True)
                    else:
                        self.clear()
                return None
            case self.piece_selected_and_dragging:
                if event.type == pg.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                    return None
                if event.type == pg.MOUSEBUTTONUP:
                    self.mouse_x, self.mouse_y = event.pos
                    pos = self.board_view.get_pos(self.mouse_x, self.mouse_y)
                    if self.legal_moves & pos != 0:
                        if self.chessboard.is_promotion(self.selected_src, pos):
                            self.promotion_square = pos
                            self.state = self.awaiting_promotion_choice
                            self.drag = False
                            return None
                        piece_type = self.chessboard.get_piece_at_pos(self.selected_src)
                        res = gl.Move(self.selected_src, pos, piece_type[1], piece_type[0])
                        self.clear()
                        return res
                    if pos & self.selected_src != 0 and self.selected_twice:
                        self.clear()
                    else:
                        self.state = self.piece_selected
                        self.drag = False
                return None
            case self.awaiting_promotion_choice:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse_x, self.mouse_y = event.pos
                    pos = self.board_view.get_pos(self.mouse_x, self.mouse_y)
                    if self.promotion_square & np.uint64(0xff) != 0:
                        for i, type in enumerate(['q', 'n', 'r', 'b']):
                            if pos & self.promotion_square << np.uint64(8 * i) != 0:
                                res = gl.Move(self.selected_src, self.promotion_square, 'p', 'b', type)
                                self.clear()
                                return res
                    if self.promotion_square & np.uint64(0xff00000000000000) != 0:
                        for i, type in enumerate(['q', 'n', 'r', 'b']):
                            if pos & self.promotion_square >> np.uint64(8 * i) != 0:
                                res = gl.Move(self.selected_src, self.promotion_square, 'p', 'w', type)
                                self.clear()
                                return res
                    self.clear()
                return None

                    
                

                        
                    



