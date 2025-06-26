"""
Module implementing the Game class
"""

import pygame as pg
from app import config as cf
from app.src.engine import chessboard, ai
from app.src.gui import boardview
from app.src.gui import inputhandler
from app.src.engine import game_logic as gl
from app.src.player.humanplayer import LocalHumanPlayer, RemoteHumanPlayer
from app.src.player.computerplayer import ComputerPlayer
from app.src.engine.clock import ChessClock


class Game:
    """
    Class representing a single running chess game
    """
    def __init__(self, display: pg.Surface):
        self.running = True
        self.display = display
        self.clock = pg.time.Clock()
        self.FPS = cf.DEFAULT_FPS
        self.chessboard = chessboard.Chessboard()

    def run(self, chessclock: ChessClock, mode: int, start_as_white: int):
        """
        Run the game based on the arguments, return a string explaining how the game ended or 
        None if the game was shut down before properly ending
        """
        self.chessclock = chessclock
        self.start_as_white = start_as_white
        match mode:
            case cf.LOCAL:
                return self.run_locally()
            case cf.AS_HOST:
                return self.run_as_host()
            case cf.AS_CLIENT:
                return self.run_as_client()
            case cf.AGAINST_COMPUTER:
                return self.run_against_computer()
            
    def run_locally(self):
        """
        Run the game locally - use mouse as input
        """
        self.board_view = boardview.BoardView(self.chessboard, self.chessclock, flip = False)
        self.player = LocalHumanPlayer(0, self.chessboard, self.board_view)
        if self.chessclock is not None:
            self.chessclock.start(self.chessboard.to_move)
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    break
                if event.type in [pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION]:
                    self.player.handle_input(event)
            if not self.running:
                break
            move = self.player.get_move()
            if move is not None:
                self.chessboard.execute_move(move)
                if self.chessclock is not None:
                    self.chessclock.press()
            else:
                if self.chessclock is not None:
                    self.chessclock.update()
            
            if self.chessclock is not None and self.chessclock.timeout:
                self.chessboard.raise_timeout()
            board = self.board_view.render_board(self.player.input_handler.get_state())
            self.display.blit(board, self.board_view.topleft)
            pg.display.flip()
            self.clock.tick(self.FPS)
            if self.chessboard.ended:
                if self.chessclock is not None:
                    self.chessclock.pause()
                return self.display_result(self.chessboard.get_result())
        return None

    def run_against_computer(self):
        """
        Run the game locally against a computer. Use mouse for input
        """
        self.board_view = boardview.BoardView(self.chessboard, self.chessclock, flip = False if self.start_as_white else True)
        self.player = LocalHumanPlayer(0 if self.start_as_white else 1, self.chessboard, self.board_view)
        self.computer = ComputerPlayer(1 if self.start_as_white else 0, self.chessboard)
        if self.chessclock is not None:
            self.chessclock.start(self.chessboard.to_move)
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    break
                if event.type in [pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION]:
                    self.player.handle_input(event, True if self.player.color != self.chessboard.to_move else False)
            if not self.running:
                break
            if self.player.color == self.chessboard.to_move:
                move = self.player.get_move()
            else:
                move = self.computer.get_move()
            if move is not None:
                self.chessboard.execute_move(move)
                if self.chessclock is not None:
                    self.chessclock.press()
            else:
                if self.chessclock is not None:
                    self.chessclock.update()

            if self.chessclock is not None and self.chessclock.timeout:
                self.chessboard.raise_timeout()
            board = self.board_view.render_board(self.player.input_handler.get_state())
            self.display.blit(board, self.board_view.topleft)
            pg.display.flip()
            if self.chessboard.ended:
                if self.chessclock is not None:
                    self.chessclock.pause()
                self.computer.stop_calculating()
                return self.display_result(self.chessboard.get_result())
        return None

 

    def display_result(self, result: int):
        """
        Return string explaining how the game ended
        """
        match result:
            case cf.DRAW_BY_INSUFFICIENT_MATERIAL:
                return "Draw by insufficient material."
            case cf.DRAW_BY_THREEFOLD_REPETITION:
                return "Draw by threefold repetition."
            case cf.DRAW_BY_50_MOVE_RULE:
                return "Draw by 50-move rule."
            case cf.DRAW_BY_STALEMATE:
                return "Draw by stalemate."
            case cf.WHITE_VICTORY_BY_CHECKMATE:
                return "White victory by checkmate."
            case cf.BLACK_VICTORY_BY_CHECKMATE:
                return "Black victory by checkmate."
            case cf.WHITE_VICTORY_BY_TIMEOUT:
                return "White victory by timeout."
            case cf.BLACK_VICTORY_BY_TIMEOUT:
                return "Black victory by timeout."
            case cf.DRAW_BY_TIMEOUT_AGAINST_INSUFFICIENT_MATERIAL:
                return "Draw by timeout against insufficient material."

                

