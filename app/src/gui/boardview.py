"""
Module implementing the boardview class
"""
from app.src.engine import game_logic as gl
from app.src.engine import chessboard
from app.src.gui import piece
import pygame as pg
from app import config as cf
import numpy as np
from app.src.engine.clock import ChessClock

class BoardView():
    """
    Class implementing methods for chessboard and chessclock rendering
    """
    def __init__(self, chessboard: chessboard.Chessboard, chessclock: ChessClock = None, flip: bool = False):
        """
        Initialize the empty chessboard surface, load piece images from filesystem, load colors and dimensions from config
        """
        self.chessboard = chessboard
        self.chessclock = chessclock
        self.flip = flip
        self.width = cf.DEFAULT_BOARD_WIDTH
        self.height = cf.DEFAULT_BOARD_HEIGHT
        self.square_width = self.width // 8
        self.square_height = self.height // 8
        self.black = cf.DARK_SQUARE_COLOR
        self.white = cf.LIGHT_SQUARE_COLOR
        self.selected_black = cf.SELECTED_DARK_SQUARE_COLOR
        self.selected_white = cf.SELECTED_LIGHT_SQUARE_COLOR
        self.legal_move_mult = cf.LEGAL_MOVE_COLOR_MULTIPLIER
        self.promotion_menu_color = cf.PROMOTION_MENU_COLOR
        self.background_color = cf.BACKGROUND_COLOR
        self.clock_black = cf.CLOCK_BLACK_COLOR
        self.clock_white = cf.CLOCK_WHITE_COLOR
        self.empty_board = self.init_empty_board()
        self.pieces = self.init_pieces()
        self.topleft = cf.DEFAULT_BOARD_TOPLEFT
        

    def get_square_rect(self, pos: np.uint64) -> tuple[pg.Rect, int]:
        """
        Return rectangle with dimensions and coordinates corresponding to the chessboard square with the arg index
        """
        idx = gl.bb_to_idx(pos)
        if self.flip:
            idx = 63 - idx
        rank = idx // 8
        file = idx % 8
        res = pg.Rect(0, 0, self.square_width, self.square_height)
        x = self.width * file // 8
        y = self.height - (self.height * rank // 8)
        res.bottomleft = (x, y)
        color = 0 if (rank + file) % 2 == 1 else 1
        return res, color    

    def init_empty_board(self) -> pg.Surface:
        """
        Initialize the empty chessboard surface
        """
        board = pg.Surface((self.width, self.height * 9 / 8))
        board.fill(self.background_color)
        for row in range(8):
            for col in range(8):
                color = self.white if (row + col) % 2 == 0 else self.black
                rect = pg.Rect(col * self.square_width, row * self.square_height, self.square_width, self.square_height)
                pg.draw.rect(board, color, rect)
        return board
    
    def init_pieces(self) -> dict[str : piece.Piece]:
        """
        Load piece images from memory, store all pieces as a dictionary of pygame Sprites
        """
        pieces = {}
        for type in cf.IMAGE_PATHS.keys():
            pieces[type] = piece.Piece(type, self.square_width, self.square_height)
        return pieces

    def render_board(self, input_handler_state: tuple) -> pg.Surface:
        """
        Render the entire chessboard with all pieces and chess clocks if they are being used based on the
        current state of the input handler provided in arg
        """
        selected_src, legal_moves, drag, promotion_square, mouse_x, mouse_y = input_handler_state
        res = self.empty_board.copy()

        selected_squares = []
        if self.chessboard.last_move_played is not None:
            selected_squares.extend([self.chessboard.last_move_played.src, self.chessboard.last_move_played.dst])
        if selected_src is not None:
            selected_squares.append(selected_src)

        for pos in selected_squares:
            rect, color = self.get_square_rect(pos)
            col = self.selected_black if color == 1 else self.selected_white
            pg.draw.rect(res, col, rect)
            
        if selected_src is not None:
            for pos in gl.generate_positions(legal_moves):
                rect, color = self.get_square_rect(pos)
                if pos in selected_squares:
                    col = self.selected_black if color == 1 else self.selected_white
                else:
                    col = self.black if color == 1 else self.white
                if pos & self.chessboard.board_state.occupied() != 0:
                    pg.draw.circle(res, tuple(int(c * self.legal_move_mult) for c in col), rect.center, rect.width // 2, width = rect.width // 12)
                else:
                    pg.draw.circle(res, tuple(int(c * self.legal_move_mult) for c in col), rect.center, rect.width // 6)                

        piece_positions = self.chessboard.board_state.get_piece_positions()
        last_to_draw_parameters = None
        for piece_type in piece_positions:
            for pos in gl.generate_positions(piece_positions[piece_type]):
                if promotion_square is not None and selected_src is not None and selected_src == pos:
                    continue
                if drag is True and selected_src is not None and selected_src == pos:
                    last_to_draw_parameters = (piece_type, mouse_x, mouse_y)
                    continue
                else:
                    idx = gl.bb_to_idx(pos)
                    if self.flip:
                        idx = 63 - idx
                    rank = idx // 8
                    file = idx % 8
                    x = self.width * file // 8
                    y = self.height - (self.height * rank // 8)
                    self.pieces[piece_type].render(x, y, res)
        if last_to_draw_parameters is not None:
            self.pieces[last_to_draw_parameters[0]].render(last_to_draw_parameters[1], last_to_draw_parameters[2], res, True)
        if self.chessclock is not None:
            res = self.render_clock(res)
        if promotion_square is not None:
            return self.render_promotion_menu(res, promotion_square)
        return res
    
    def render_promotion_menu(self, board: pg.Surface, promotion_square: np.uint64) -> pg.Surface:
        """
        Render the promotion menu into the chessboard at the respective promotion square
        """
        if promotion_square & np.uint64(0xff) != 0:
            for i, type in enumerate(['bq', 'bn', 'br', 'bb']):
                pos = promotion_square << np.uint64(i * 8)
                rect, _ = self.get_square_rect(pos)
                pg.draw.rect(board, self.promotion_menu_color, rect)
                self.pieces[type].render(rect.bottomleft[0], rect.bottomleft[1], board)
            return board
        for i, type in enumerate(['wq', 'wn', 'wr', 'wb']):
            pos = promotion_square >> np.uint64(i * 8)
            rect, _ = self.get_square_rect(pos)
            pg.draw.rect(board, self.promotion_menu_color, rect)
            self.pieces[type].render(rect.bottomleft[0], rect.bottomleft[1], board)
        return board
    
    def get_pos(self, x: int, y: int) -> np.uint64:
        """
        Return bitboard of the position of the chess square containing the pixel with (x, y) coordinates from the arg
        """
        x -= self.topleft[0]
        y -= self.topleft[1]
        if (x not in range(self.width) or y not in range(self.height)):
            return np.uint64(0)
        if self.flip:
            rank = y // self.square_height
            file = 7 - (x // self.square_width)
        else:
            rank = 7 - (y // self.square_height)
            file = x // self.square_width
        pos = np.uint64(1 << (rank * 8 + file))
        return pos
    
    def render_clock(self, board: pg.Surface) -> pg.Surface:
        """
        Render the chess clocks under the chessboard
        """
        times = self.chessclock.get_player_times()
        font = pg.font.SysFont(cf.DEFAULT_FONT, int(self.height / 18), True)
        white_time = font.render(times[0], True, self.clock_black)
        white_rect = pg.rect.Rect(0, 0, self.square_width * 2, self.square_height * 3 / 4)
        white_rect.bottomright = (self.width, self.height * 9 / 8)
        pg.draw.rect(board, self.clock_white, white_rect)
        white_time_rect = white_time.get_rect(center = white_rect.center)
        board.blit(white_time, white_time_rect)

        black_time = font.render(times[1], True, self.clock_white)
        black_rect = pg.rect.Rect(0, 0, self.square_width * 2, self.square_height * 3 / 4)
        black_rect.bottomleft = (0, self.height * 9 / 8)
        pg.draw.rect(board, self.clock_black, black_rect)
        black_time_rect = black_time.get_rect(center = black_rect.center)
        board.blit(black_time, black_time_rect)
        return board
        
        


        

    



