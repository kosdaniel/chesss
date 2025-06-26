"""
Module for the AI class
"""

from app.src.engine import game_logic as gl, chessboard
from app import config as cf
import threading
from copy import deepcopy

class AI():
    """
    Class used for calculating chess moves
    """
    def __init__(self):
        self.calculated_move = None
        self.running_thread = None
        self.running = True

    def poll_for_move(self, chessboard: chessboard.Chessboard):
        """
        Returns the currently calculated move if there is one, else returns None
        If there is no calculated move and no move is being calculated, starts calculating a new move
        """
        if not self.running:
            return None
        if self.calculated_move is not None:
            res = self.calculated_move
            self.calculated_move = None
            return res
        if self.running_thread is None:
            self.calculate_best_move(chessboard)
        return None

    def quit(self):
        """
        Disallows further calculation of moves
        """
        self.running = False

    def minimax(self, chessboard: chessboard.Chessboard, depth: int = cf.DEFAULT_SEARCH_DEPTH) -> tuple[int, gl.Move | None]:
        """
        Basic minimax algorithm with no performance boosts
        inspired by https://www.youtube.com/watch?v=l-hh51ncgDI&ab_channel=SebastianLague
        Takes a Chessboard object and max search depth as args, returns a move maximizing material count heuristic for the 
        respective player color on move and always preferring moves leading to checkmate. This algorithm doesnt prefer 
        moves leading to faster checkmate and might fail to deliver checkmate in special instances
        """
        if depth == 0 or chessboard.ended:
            return chessboard.get_position_evaluation(), chessboard.last_move_played

        if chessboard.to_move == 0:
            max_eval = -cf.INF
            for move in chessboard.get_all_legal_moves():
                board_copy = deepcopy(chessboard)
                board_copy.execute_move(move)
                eval, _ = self.minimax(board_copy, depth - 1)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move

        min_eval = cf.INF
        for move in chessboard.get_all_legal_moves():
            board_copy = deepcopy(chessboard)
            board_copy.execute_move(move)
            eval, _ = self.minimax(board_copy, depth - 1)
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move

    def minimax_with_pruning(self, board_state: gl.BoardState, to_move: int, depth: int = cf.DEFAULT_SEARCH_DEPTH, initial_depth = None,
                            alpha: int = -cf.INF, beta: int = cf.INF) -> tuple[int, gl.Move | None]:
        """
        Minimax algorithm with alpha-beta pruning, uses only the raw BoardState object instead of the Chessboard object 
        and limits the calculation of legal moves to a minimum to boost performance.
        Takes a board state, player color and max depth as arguments, returns a move maximizing/minimizing material count 
        heuristic based on color, always preferring moves that lead to the fastest checkmate.
        Also inspired by https://www.youtube.com/watch?v=l-hh51ncgDI&ab_channel=SebastianLague
        """
        if initial_depth is None:
            initial_depth = depth
        best_move = None
        no_legal_moves = True
        if to_move == 0:
            final_eval = -cf.INF
            for move in board_state.get_all_pseudo_legal_moves(to_move):
                board_copy = deepcopy(board_state)
                if not board_copy.push_move(move, pseudo_legality_check = False) or board_copy.king_in_check(to_move):
                    continue
                no_legal_moves = False
                if depth == 0:
                    break
                eval, _ = self.minimax_with_pruning(board_copy, 1 - to_move, depth - 1, initial_depth, alpha, beta)
                if eval > final_eval:
                    final_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        else:
            final_eval = cf.INF
            for move in board_state.get_all_pseudo_legal_moves(to_move):
                board_copy = deepcopy(board_state)
                if not board_copy.push_move(move, pseudo_legality_check = False) or board_copy.king_in_check(to_move):
                    continue
                no_legal_moves = False
                if depth == 0:
                    break
                eval, _ = self.minimax_with_pruning(board_copy, 1 - to_move, depth - 1, initial_depth, alpha, beta)
                if eval < final_eval:
                    final_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        if depth == 0 and not no_legal_moves:
            return board_state.get_material_count(0) - board_state.get_material_count(1), best_move
        if no_legal_moves:
            if board_state.king_in_check(to_move):
                return ((cf.INF - initial_depth + depth) if to_move == 1 else (-cf.INF + initial_depth - depth)), best_move
            return 0, best_move
        return final_eval, best_move


    def execute_minimax(self, chessboard:chessboard.Chessboard):
        """
        Creates a new thread and calls the minimax function on it, stores the resulting move
        """
        _, self.calculated_move = self.minimax(chessboard)
        self.running_thread = None

    def execute_minimax_with_pruning(self, chessboard:chessboard.Chessboard):
        """
        Creates a new thread and calls the minimax with pruning function on it, stores the resulting move
        """
        board_state = deepcopy(chessboard.board_state)
        to_move = chessboard.to_move
        _, self.calculated_move = self.minimax_with_pruning(board_state, to_move)
        if self.calculated_move is None and not chessboard.ended:
            self.calculated_move = chessboard.get_all_legal_moves()[0]
        self.running_thread = None

    def calculate_best_move(self, chessboard: chessboard.Chessboard):
        """
        If no move is currently being calculated, calls the execute minimax with pruning function
        """
        if self.running_thread is not None:
            return
        self.running_thread = threading.Thread(target = self.execute_minimax_with_pruning, args = (chessboard,))
        self.running_thread.start()