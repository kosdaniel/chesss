"""
Module implementing the chessboard class
"""
from app.src.engine import game_logic as gl
from app import config as cf
from copy import deepcopy
import numpy as np


class Chessboard():
    """
    Class representing a chessboard / higher abstraction of the board state class
    Manages who is on move, checks for end of game
    """
    def __init__(self, fen: str = cf.STARTING_POSITION_FEN):
        """
        Initialize the chessboard instance from a full valid fen string
        """
        self.board_state = gl.BoardState(fen)
        fen_parts = fen.split(' ')
        match fen_parts[1]:
            case 'w':
                self.to_move = 0
            case 'b':
                self.to_move = 1
        self.half_move_count = int(fen_parts[4])
        self.full_move_count = int(fen_parts[5])
        self.ended = False
        self.reached_positions = {}
        self.last_move_played = None
        self.no_legal_moves = False
        self.timeout = False

        
    def validate_move(self, move: gl.Move) -> bool:
        """
        Return true if the arg move is legal else false
        """
        if move.src & self.board_state.occupied(self.to_move) == 0:
            return False
        board_state_copy = deepcopy(self.board_state)
        return board_state_copy.push_move(move) and not board_state_copy.king_in_check(self.to_move)
    
    def get_legal_moves(self, pos: np.uint64, return_as_bitboard: bool = False) -> list[gl.Move] | np.uint64: 
        """
        Return list of all legal moves from the given position or 
        bitboard of all legal move destinations from the given position
        """
        if pos & self.board_state.occupied(self.to_move) == 0:
            if return_as_bitboard:
                return np.uint64(0)
            return []
        pseudo_legal_moves = self.board_state.pos_moves(pos)
        res = []
        for move in pseudo_legal_moves:
            if self.validate_move(move):
                res.append(move)
        if return_as_bitboard:
            bb = np.uint64(0)
            for move in res:
                bb |= move.dst
            return bb
        return res
    
    def get_all_legal_moves(self) -> list[gl.Move]:
        """
        Return a list of all legal moves that can be played by the player on move
        """
        res = []
        for pos in gl.generate_positions(self.board_state.occupied(self.to_move)):
            res.extend(self.get_legal_moves(pos))
        return res
    
    def get_position_evaluation(self) -> int:
        """
        Return numerical evaluation of the current position
        """
        result = self.get_result()
        if result == -1:
            return self.board_state.get_material_count(0) - self.board_state.get_material_count(1)
        if result == cf.WHITE_VICTORY_BY_CHECKMATE:
            return cf.INF
        if result == cf.BLACK_VICTORY_BY_CHECKMATE:
            return -cf.INF
        return 0
    
        
    def has_ended(self) -> bool:
        """
        Return true if the game has ended else false
        """
        if self.timeout: 
            return True
        if self.get_all_legal_moves() == []:
            self.no_legal_moves = True
            return True
        if self.half_move_count >= 100:
            return True
        if self.board_state.has_insufficient_material(0) and self.board_state.has_insufficient_material(1):
            return True
        for count in self.reached_positions.values():
            if count >= 3:
                return True
        return False        

    def get_result(self) -> int:
        """
        Return result of the game or -1 if it has not ended yet
        """
        if self.timeout:
            if self.to_move == 0:
                if self.board_state.has_insufficient_material(1):
                    return cf.DRAW_BY_TIMEOUT_AGAINST_INSUFFICIENT_MATERIAL
                return cf.BLACK_VICTORY_BY_TIMEOUT
            else:
                if self.board_state.has_insufficient_material(0):
                    return cf.DRAW_BY_TIMEOUT_AGAINST_INSUFFICIENT_MATERIAL
                return cf.WHITE_VICTORY_BY_TIMEOUT
        if not self.ended:
            return -1
        if self.no_legal_moves:
            if self.board_state.king_in_check(self.to_move):
                if self.to_move == 0:
                    return cf.BLACK_VICTORY_BY_CHECKMATE
                return cf.WHITE_VICTORY_BY_CHECKMATE
            return cf.DRAW_BY_STALEMATE
        if self.board_state.has_insufficient_material(0) and self.board_state.has_insufficient_material(1):
            return cf.DRAW_BY_INSUFFICIENT_MATERIAL
        for count in self.reached_positions.values():
            if count >= 3:
                return cf.DRAW_BY_THREEFOLD_REPETITION
        return cf.DRAW_BY_50_MOVE_RULE
    
    def execute_move(self, move: gl.Move, validate: bool = False) -> bool:
        """
        Play given move in argument, return true if move is legal and has been succesfully pushed else false
        """
        if self.ended or (validate and not self.validate_move(move)):
            return False
        if self.to_move == 0:
            self.to_move = 1
        else:
            self.to_move = 0
            self.full_move_count += 1
        if self.board_state.is_pawn_or_capture(move):
            self.half_move_count = 0
        else:
            self.half_move_count += 1
        self.board_state.push_move(move)
        position_hash = self.board_state.get_position_hash(self.to_move)
        self.reached_positions[position_hash] = self.reached_positions.get(position_hash, 0) + 1
        self.ended = self.has_ended()
        self.last_move_played = move
        return True
        
    def get_piece_at_pos(self, pos: np.uint64) -> str | None:
        """
        Return type and color of piece at the arg pos
        """
        return self.board_state.get_piece_type(pos)
        
    def is_promotion(self, src: np.uint64, dst: np.uint64) -> bool:
        """
        Return true if the move from the arg source to the arg destination is a promotion else false
        """
        return self.get_piece_at_pos(src) in ['wp', 'bp'] and dst & np.uint64(0xff000000000000ff) != 0
    
    def raise_timeout(self):
        """
        End the game and raise timeout flag
        """
        self.timeout = True
        self.ended = True
        
        
        
