"""
Module implementing all necessary backend logic for a chess engine
"""

from app import config as cf
import numpy as np
import random

class Move:
    """
    Basic data class representing a single chess move
    """
    def __init__(self, src: np.uint64, dst: np.uint64, type: str, color: str, promotion_type: str = None):
        self.src = src
        self.dst = dst
        self.type = type
        self.color = color
        self.promotion_type = promotion_type
        

class BoardState():
    """
    Class representing a single board state and implementing all necessary associated methods
    """
    def __init__(self, fen: str = cf.STARTING_POSITION_FEN):
        """
        BoardState takes a valid fen string as a constructor argument
        """
        self.pieces = {
            'wp' : np.uint64(0),
            'wn' : np.uint64(0),
            'wb' : np.uint64(0),
            'wr' : np.uint64(0),
            'wq' : np.uint64(0),
            'wk' : np.uint64(0),
            'bp' : np.uint64(0),
            'bn' : np.uint64(0),
            'bb' : np.uint64(0),
            'br' : np.uint64(0),
            'bq' : np.uint64(0),
            'bk' : np.uint64(0),
        }

        self.en_passant_square = np.uint64(0)
        self.black_oo = False
        self.black_ooo = False
        self.white_oo = False
        self.white_ooo = False

        self.init(fen)                

    def init(self, fen: str) -> None:
        """
        Parse fen string and initialize piece positions, castling rights and 
        the potential en passant target square accordingly
        """
        fen_parts = fen.split(' ')
        board_fen = fen_parts[0]
        for i, rank in enumerate(board_fen.split('/')):
            file = 0
            for char in rank:
                if char.isdigit():
                    file += int(char)
                    continue
                pos = idx_to_bb(file + (7 - i) * 8)
                match char:
                    case 'p':
                        self.pieces['bp'] |= pos
                    case 'n':
                        self.pieces['bn'] |= pos
                    case 'b':
                        self.pieces['bb'] |= pos
                    case 'r':
                        self.pieces['br'] |= pos
                    case 'q':
                        self.pieces['bq'] |= pos
                    case 'k':
                        self.pieces['bk'] |= pos
                    case 'P':
                        self.pieces['wp'] |= pos
                    case 'N':
                        self.pieces['wn'] |= pos
                    case 'B':
                        self.pieces['wb'] |= pos
                    case 'R':
                        self.pieces['wr'] |= pos
                    case 'Q':
                        self.pieces['wq'] |= pos
                    case 'K':
                        self.pieces['wk'] |= pos
                file += 1
        
        for char in fen_parts[2]:
            match char:
                case '-':
                    break
                case 'K':
                    self.white_oo = True
                case 'Q':
                    self.white_ooo = True
                case 'k':
                    self.black_oo = True
                case 'q':
                    self.black_ooo = True
        
        if fen_parts[3] != '-':
            self.en_passant_square = idx_to_bb(pos_to_idx(fen_parts[3]))
        
        
    def occupied(self, color: int = None) -> np.uint64:
        """
        Return a bitboard with bits set to 1 if the square with associated index is occupied,
        if no argument is provided, by pieces of either color, else only pieces of the color in the argument 
        """
        if color is None:
            return (self.pieces['wp'] | self.pieces['wn'] | self.pieces['wb'] | self.pieces['wr'] |
                    self.pieces['wq'] | self.pieces['wk'] | self.pieces['bp'] | self.pieces['bn'] |
                    self.pieces['bb'] | self.pieces['br'] | self.pieces['bq'] | self.pieces['bk'])
        elif color == 0:
            return (self.pieces['wp'] | self.pieces['wn'] | self.pieces['wb'] | self.pieces['wr'] |
                    self.pieces['wq'] | self.pieces['wk'])
        else:
            return (self.pieces['bp'] | self.pieces['bn'] | self.pieces['bb'] | self.pieces['br'] |
                    self.pieces['bq'] | self.pieces['bk'])
    
    def pawn_moves(self, pos: np.uint64) -> np.uint64:
        """
        Return a bitboard with bits set to 1 for all possible pawn moves from the position in the argument
        """
        idx = bb_to_idx(pos)
        res = np.uint64(0)
        if pos & self.pieces['wp'] != 0:
            res |= pos << np.uint64(8) & ~self.occupied()
            if pos & np.uint64(0xff00) != 0 and res != 0:
                res |= (pos << np.uint64(16)) & ~self.occupied()
            if idx % 8 != 0:
                res |= (pos << np.uint64(7)) & (self.occupied(1) | self.en_passant_square)
            if idx % 8 != 7:
                res |= (pos << np.uint64(9)) & (self.occupied(1) | self.en_passant_square)
            return res
        res |= pos >> np.uint64(8) & ~self.occupied()
        if pos & np.uint64(0xff000000000000) != 0 and res != 0:
            res |= (pos >> np.uint64(16)) & ~self.occupied()
        if idx % 8 != 0:
            res |= (pos >> np.uint64(9)) & (self.occupied(0) | self.en_passant_square)
        if idx % 8 != 7:
            res |= (pos >> np.uint64(7)) & (self.occupied(0) | self.en_passant_square)
        return res
        

    def bishop_moves(self, pos: np.uint64, queen: bool = False) -> np.uint64:
        """
        Return a bitboard with bits set to 1 for all possible bishop moves from the position in the argument
        """
        if (not queen and pos & self.pieces['wb'] != 0) or (queen and pos & self.pieces['wq'] != 0):
            friendly_color = 0
            enemy_color = 1
        else:
            friendly_color = 1
            enemy_color = 0
        res = np.uint64(0)
        idx = bb_to_idx(pos)
        tmp_pos = pos
        tmp_idx = idx
        while True:
            rank = tmp_idx // 8
            file = tmp_idx % 8
            if file == 7 or rank == 7:
                break
            tmp_idx += 9
            tmp_pos = tmp_pos << np.uint64(9)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos
        tmp_pos = pos
        tmp_idx = idx
        while True:
            rank = tmp_idx // 8
            file = tmp_idx % 8
            if file == 7 or rank == 0:
                break
            tmp_idx -= 7
            tmp_pos = tmp_pos >> np.uint64(7)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos    
        tmp_pos = pos
        tmp_idx = idx
        while True:
            rank = tmp_idx // 8
            file = tmp_idx % 8
            if file == 0 or rank == 7:
                break
            tmp_idx += 7
            tmp_pos = tmp_pos << np.uint64(7)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos
        tmp_pos = pos
        tmp_idx = idx
        while True:
            rank = tmp_idx // 8
            file = tmp_idx % 8
            if file == 0 or rank == 0:
                break
            tmp_idx -= 9
            tmp_pos = tmp_pos >> np.uint64(9)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos
        return res

    def rook_moves(self, pos: np.uint64, queen: bool = False) -> np.uint64:
        """
        Return a bitboard with bits set to 1 for all possible rook moves from the position in the argument
        """
        if (not queen and pos & self.pieces['wr'] != 0) or (queen and pos & self.pieces['wq'] != 0):
            friendly_color = 0
            enemy_color = 1
        else:
            friendly_color = 1
            enemy_color = 0
        res = np.uint64(0)
        idx = bb_to_idx(pos)
        tmp_pos = pos
        tmp_idx = idx
        while True:
            rank = tmp_idx // 8
            if rank == 7:
                break
            tmp_idx += 8
            tmp_pos = tmp_pos << np.uint64(8)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos
        tmp_pos = pos
        tmp_idx = idx
        while True:
            rank = tmp_idx // 8
            if rank == 0:
                break
            tmp_idx -= 8
            tmp_pos = tmp_pos >> np.uint64(8)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos
        tmp_pos = pos
        tmp_idx = idx
        while True:
            file = tmp_idx % 8
            if file == 7:
                break
            tmp_idx += 1
            tmp_pos = tmp_pos << np.uint64(1)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos
        tmp_pos = pos
        tmp_idx = idx
        while True:
            file = tmp_idx % 8
            if file == 0:
                break
            tmp_idx -= 1
            tmp_pos = tmp_pos >> np.uint64(1)
            if self.occupied(friendly_color) & tmp_pos != 0:
                break
            if self.occupied(enemy_color) & tmp_pos != 0:
                res |= tmp_pos
                break
            res |= tmp_pos        
        return res
        
    def queen_moves(self, pos: np.uint64) -> np.uint64:
        """
        Return a bitboard with bits set to 1 for all possible queen moves from the position in the argument
        """
        return self.rook_moves(pos, True) | self.bishop_moves(pos, True)
    
    def knight_moves(self, pos: np.uint64) -> np.uint64:
        """
        Return a bitboard with bits set to 1 for all possible knight moves from the position in the argument
        """
        res = np.uint64(0)
        if pos & self.pieces['wn'] != 0:
            friendly_color = 0
        else:
            friendly_color = 1
        
        a_file = np.uint64(0x0101010101010101)
        b_file = np.uint64(0x0202020202020202)
        g_file = np.uint64(0x4040404040404040)
        h_file = np.uint64(0x8080808080808080)
        rank_1 = np.uint64(0x00000000000000ff)
        rank_2 = np.uint64(0x000000000000ff00)
        rank_7 = np.uint64(0x00ff000000000000)
        rank_8 = np.uint64(0xff00000000000000)

        occupied = self.occupied(friendly_color)

        if pos & ~rank_7 & ~rank_8 & ~a_file != 0:
            res |= pos << np.uint64(15) & ~occupied
        if pos & ~rank_7 & ~rank_8 & ~h_file != 0:
            res |= pos << np.uint64(17) & ~occupied
        if pos & ~rank_8 & ~g_file & ~h_file != 0:
            res |= pos << np.uint64(10) & ~occupied
        if pos & ~rank_1 & ~g_file & ~h_file != 0:
            res |= pos >> np.uint64(6) & ~occupied
        if pos & ~rank_1 & ~rank_2 & ~h_file != 0:
            res |= pos >> np.uint64(15) & ~occupied
        if pos & ~rank_1 & ~rank_2 & ~a_file != 0:
            res |= pos >> np.uint64(17) & ~occupied
        if pos & ~rank_1 & ~a_file & ~b_file != 0:
            res |= pos >> np.uint64(10) & ~occupied
        if pos & ~rank_8 & ~a_file & ~b_file != 0:
            res |= pos << np.uint64(6) & ~occupied

        return res


    def king_moves(self, pos: np.uint64, castling: bool = True) -> np.uint64:
        """
        Return a bitboard with bits set to 1 for all possible king moves from the position in the argument
        Ignore checking for castling possibilities if castling arg set to False - used by other methods to avoid recursion
        """
        res = np.uint64(0)
        if pos & self.pieces['wk'] != 0:
            friendly_color = 0
            if castling:
                attacked_squares = self.attacked_squares_by_black()
                if (self.white_oo and attacked_squares & np.uint64(0x70) == 0 and 
                self.occupied() & np.uint64(0x60) == 0 and self.pieces['wr'] & idx_to_bb(7) != 0):
                    res |= np.uint64(1 << 6)
                if (self.white_ooo and attacked_squares & np.uint64(0x1c) == 0 and 
                self.occupied() & np.uint64(0x0c) == 0 and self.pieces['wr'] & idx_to_bb(0) != 0):
                    res |= np.uint64(1 << 2)
        else:
            friendly_color = 1
            if castling:
                attacked_squares = self.attacked_squares_by_white()
                if (self.black_oo and attacked_squares & np.uint64(0x7000000000000000) == 0 and 
                self.occupied() & np.uint64(0x6000000000000000) == 0 and self.pieces['br'] & idx_to_bb(63) != 0):
                    res |= np.uint64(1 << 62)
                if (self.black_ooo and attacked_squares & np.uint64(0x1c00000000000000) == 0 and 
                    self.occupied() & np.uint64(0x0c00000000000000) == 0 and self.pieces['br'] & idx_to_bb(56) != 0):
                    res |= np.uint64(1 << 58)
        
        a_file = np.uint64(0x0101010101010101)
        h_file = np.uint64(0x8080808080808080)
        rank_1 = np.uint64(0x00000000000000ff)
        rank_8 = np.uint64(0xff00000000000000)

        occupied = self.occupied(friendly_color)

        if pos & ~rank_8 != 0:
            res |= pos << np.uint64(8) & ~occupied
        if pos & ~rank_1 != 0:
            res |= pos >> np.uint64(8) & ~occupied
        if pos & ~h_file != 0:
            res |= pos << np.uint64(1) & ~occupied
        if pos & ~a_file != 0:
            res |= pos >> np.uint64(1) & ~occupied
        if pos & ~rank_8 & ~a_file != 0:
            res |= pos << np.uint64(7) & ~occupied
        if pos & ~rank_8 & ~h_file != 0:
            res |= pos << np.uint64(9) & ~occupied
        if pos & ~rank_1 & ~a_file != 0:
            res |= pos >> np.uint64(9) & ~occupied
        if pos & ~rank_1 & ~h_file != 0:
            res |= pos >> np.uint64(7) & ~occupied
        return res
    
    def pos_moves(self, pos: np.uint64) -> list[Move]:
        """
        Return a list of all possible moves from the position in arg
        """
        piece_type = self.get_piece_type(pos)
        if piece_type is None:
            return []
        moves = self.pos_targets(pos)
        res = []
        if piece_type[1] != 'p' or moves & np.uint64(0xff000000000000ff) == 0:
            for dst in generate_positions(moves):
                res.append(Move(pos, dst, piece_type[1], piece_type[0]))
        else:
            for dst in generate_positions(moves):
                for promotion_type in ['q', 'b', 'n', 'r']:
                    res.append(Move(pos, dst, piece_type[1], piece_type[0], promotion_type))
        return res

    def pos_targets(self, pos: np.uint64) -> np.uint64:
        """
        Return a biboard of all possible move destinations from the given position
        """
        if pos & (self.pieces['bp'] | self.pieces['wp']) != 0:
            return self.pawn_moves(pos)
        elif pos & (self.pieces['bb'] | self.pieces['wb']) != 0:
            return self.bishop_moves(pos)
        elif pos & (self.pieces['bk'] | self.pieces['wk']) != 0:
            return self.king_moves(pos)
        elif pos & (self.pieces['bn'] | self.pieces['wn']) != 0:
            return self.knight_moves(pos)
        elif pos & (self.pieces['bq'] | self.pieces['wq']) != 0:
            return self.queen_moves(pos)
        elif pos & (self.pieces['br'] | self.pieces['wr']) != 0:
            return self.rook_moves(pos)
        return np.uint64(0)

    def get_all_pseudo_legal_moves(self, to_move: int) -> list[Move]:
        """
        Return a list of all possible pseudo-legal moves for the player color provided in the argument
        ordered in a specific way
        This method is only used in move search algorithm for performance purposes
        """
        res = []
        if to_move == 0:
            col = 'w'
        else:
            col = 'b'
        for type in ['p', 'n', 'b', 'q', 'r', 'k']:
            for pos in generate_positions(self.pieces[col + type]):
                moves = self.pos_moves(pos)
                random.shuffle(moves)
                res.extend(moves)
        return res

    def attacked_squares_by_black(self) -> np.uint64:
        """
        Return a bitboard of all squares currently being attacked by black pieces
        """
        res = np.uint64(0)
        for pos in generate_positions(self.pieces['bp']):
            res |= self.pawn_moves(pos)
        for pos in generate_positions(self.pieces['bb']):
            res |= self.bishop_moves(pos)
        for pos in generate_positions(self.pieces['bn']):
            res |= self.knight_moves(pos)
        for pos in generate_positions(self.pieces['bq']):
            res |= self.queen_moves(pos)
        for pos in generate_positions(self.pieces['bk']):
            res |= self.king_moves(pos, castling = False)
        for pos in generate_positions(self.pieces['br']):
            res |= self.rook_moves(pos)
        return res
    
    def attacked_squares_by_white(self) -> np.uint64:
        """
        Return a bitboard of all squares currently being attacked by black pieces
        """
        res = np.uint64(0)
        for pos in generate_positions(self.pieces['wp']):
            res |= self.pawn_moves(pos)
        for pos in generate_positions(self.pieces['wb']):
            res |= self.bishop_moves(pos)
        for pos in generate_positions(self.pieces['wn']):
            res |= self.knight_moves(pos)
        for pos in generate_positions(self.pieces['wq']):
            res |= self.queen_moves(pos)
        for pos in generate_positions(self.pieces['wk']):
            res |= self.king_moves(pos, castling = False)
        for pos in generate_positions(self.pieces['wr']):
            res |= self.rook_moves(pos)
        return res
    
    def delete_piece(self, pos: np.uint64):
        """
        Delete the piece occupying the arg position
        """
        for key in self.pieces:
            self.pieces[key] &= ~pos
    
    def add_piece(self, color: str, type: str, pos: np.uint64):
        """
        Add piece of given type and color to the target position
        """
        self.pieces[color + type] |= pos

    def move_piece(self, src: np.uint64, dst: np.uint64):
        """
        Move piece from the source position to the destination position
        """
        type = self.get_piece_type(src)
        if type is not None:
            self.delete_piece(src)
            self.add_piece(type[0], type[1], dst)

    def push_move(self, move: Move, pseudo_legality_check: bool = True) -> bool:
        """
        Push given move to the current board state and update the state accordingly.
        Do not check pseudo-legality of the move in argument if pseudo legality check flag is False-
        used in other methods for performance if pseudo legality check was already performed elsewhere
        """
        if pseudo_legality_check and move.dst & self.pos_targets(move.src) == 0:
            return False
        src_idx = bb_to_idx(move.src)
        dst_idx = bb_to_idx(move.dst)
        if dst_idx == 63 and self.black_oo:
            self.black_oo = False
        elif dst_idx == 56 and self.black_ooo:
            self.black_ooo = False
        elif dst_idx == 0 and self.white_ooo:
            self.white_ooo = False
        elif dst_idx == 7 and self.white_oo:
            self.white_oo = False
        en_passant = False
        capture_square = move.dst
        if move.type == 'p' and move.color == 'w':
            if dst_idx - src_idx == 16:
                self.en_passant_square = move.dst >> np.uint64(8)
                en_passant = True
            elif (dst_idx - src_idx == 7 or dst_idx - src_idx == 9) and self.en_passant_square == move.dst:
                capture_square = move.dst >> np.uint64(8)
            self.delete_piece(capture_square)

            if dst_idx // 8 == 7:
                self.delete_piece(move.src)
                self.add_piece(move.color, move.promotion_type, move.dst)
            else:
                self.move_piece(move.src, move.dst)            
                        
        elif move.type == 'p' and move.color == 'b':
            if dst_idx - src_idx == -16:
                self.en_passant_square = move.dst << np.uint64(8)
                en_passant = True
            elif (dst_idx - src_idx == -7 or dst_idx - src_idx == -9) and self.en_passant_square == move.dst:
                capture_square = move.dst << np.uint64(8)
            self.delete_piece(capture_square)
            if dst_idx // 8 == 0:
                self.delete_piece(move.src)
                self.add_piece(move.color, move.promotion_type, move.dst)
            else:
                self.move_piece(move.src, move.dst)

        else:
            self.delete_piece(move.dst)
            self.move_piece(move.src, move.dst)
        if not en_passant:
            self.en_passant_square = np.uint64(0)
            
        if move.type == 'k' and move.color == 'w':
            if src_idx == 4 and dst_idx == 6:
                self.move_piece(np.uint64(1 << 7), np.uint64(1 << 5))
            elif src_idx == 4 and dst_idx == 2:
                self.move_piece(np.uint64(1), np.uint64(1 << 3))
            self.white_oo = False
            self.white_ooo = False
        
        elif move.type == 'k' and move.color == 'b':
            if src_idx == 60 and dst_idx == 62:
                self.move_piece(np.uint64(1 << 63), np.uint64(1 << 61))
            elif src_idx == 60 and dst_idx == 58:
                self.move_piece(np.uint64(1 << 56), np.uint64(1 << 59))
            self.black_oo = False
            self.black_ooo = False

        elif move.type == 'r' and move.color == 'w':
            if self.white_oo and src_idx == 7:
                self.white_oo = False
            elif self.white_ooo and src_idx == 0:
                self.white_ooo = False            
        
        elif move.type == 'r' and move.color == 'b':
            if self.black_oo and src_idx == 63:
                self.black_oo = False
            elif self.black_ooo and src_idx == 56:
                self.black_ooo = False
        
        return True

    def king_in_check(self, color: int) -> bool:
        """
        Return true if king of target color is in check else false
        """
        if color == 0:
            return self.pieces['wk'] & self.attacked_squares_by_black() != 0
        return self.pieces['bk'] & self.attacked_squares_by_white() != 0
    
    def get_material_count(self, color: int) -> int:
        """
        Return sum of values of all pieces of the arg color.
        """
        if color == 0:
            return (int(self.pieces['wb']).bit_count() * 3 + int(self.pieces['wp']).bit_count() + int(self.pieces['wr']).bit_count() * 5 + 
                    int(self.pieces['wn']).bit_count() * 3 + int(self.pieces['wq']).bit_count() * 9)
        return (int(self.pieces['bb']).bit_count() * 3 + int(self.pieces['bp']).bit_count() + int(self.pieces['br']).bit_count() * 5 + 
                int(self.pieces['bn']).bit_count() * 3 + int(self.pieces['bq']).bit_count() * 9)
            
    def has_insufficient_material(self, color: int) -> bool:
        """
        Return true if the player of arg color has insufficient amount of material to force checkmate else false
        """
        if color == 0:
            return self.get_material_count(color) < 4 and self.pieces['wp'] == 0
        return self.get_material_count(color) < 4 and self.pieces['bp'] == 0
    
    def get_position_hash(self, color: int) -> int:
        """
        Return hash of the current board state, used by other methods for threefold repetition checks
        """
        return hash((
            self.pieces['wp'], self.pieces['wn'], self.pieces['wb'], 
            self.pieces['wr'], self.pieces['wq'], self.pieces['wk'], 
            self.pieces['bp'], self.pieces['bn'], self.pieces['bb'], 
            self.pieces['br'], self.pieces['bq'], self.pieces['bk'], 
            self.en_passant_square, color,
            self.black_oo, self.black_ooo,
            self.white_oo, self.white_ooo
        ))

    def is_pawn_or_capture(self, move: Move) -> bool:
        """
        Return true if the given move is a pawn push or a capture
        Used by other methods to properly check for 50-move draws
        """
        if move.type == 'p':
            return True
        if move.dst & self.occupied() != 0:
            return True
        return False
    
    def get_piece_positions(self) -> dict[str : np.uint64]:
        """
        Return positions of all pieces
        """
        return self.pieces
    
    def get_piece_type(self, pos: np.uint64) -> str | None:
        """
        Return color and type of the piece occupying the arg position or None if pos is empty
        """
        for key in self.pieces:
            if self.pieces[key] & pos != 0:
                return key
        return None


def pos_to_idx(pos: str) -> int:
    """
    Return index in range 0-63 of the square in argument given in algebraic notation
    """
    if pos[0] not in (chr(i) for i in range(ord('a'), ord('h') + 1)) or int(pos[1]) not in range(1, 9):
            raise ValueError('Invalid board pos argument')
    return ord(pos[0]) - ord('a') + (int(pos[1]) - 1) * 8

def idx_to_pos(idx: int) -> str:
    """
    Return square index in algebraic notation of the square with arg idx in range 0-63
    """
    if not idx in range(0, 64):
        raise ValueError('Invalid tile number argument')
    return chr(ord('a') + int(idx % 8)) + str(int(1 + (idx / 8)))

def bb_to_idx(bb: np.uint64) -> int:
    """
    Return index of the most significant bit set to 1 in the arg bitboard
    """
    return int(bb).bit_length() - 1

def idx_to_bb(idx: int) -> np.uint64:
    """
    Return bitboard with the bit at the arg index set to 1
    """
    return np.uint64(1 << idx)

def generate_positions(positions: np.uint64):
    """
    Generate bitboards with a single bit set to 1 at a given index for every bit set to 1 
    at this index in the bitboard from argument
    """
    while positions != 0:
        cur = np.uint64(1 << bb_to_idx(positions))
        yield cur
        positions ^= cur

