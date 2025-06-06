import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

BB_PATH = os.path.join(ASSETS_DIR, "bb.png")
BK_PATH = os.path.join(ASSETS_DIR, "bk.png")
BN_PATH = os.path.join(ASSETS_DIR, "bn.png")
BP_PATH = os.path.join(ASSETS_DIR, "bp.png")
BQ_PATH = os.path.join(ASSETS_DIR, "bq.png")
BR_PATH = os.path.join(ASSETS_DIR, "br.png")
WB_PATH = os.path.join(ASSETS_DIR, "wb.png")
WK_PATH = os.path.join(ASSETS_DIR, "wk.png")
WN_PATH = os.path.join(ASSETS_DIR, "wn.png")
WP_PATH = os.path.join(ASSETS_DIR, "wp.png")
WQ_PATH = os.path.join(ASSETS_DIR, "wq.png")
WR_PATH = os.path.join(ASSETS_DIR, "wr.png")

IMAGE_PATHS = {
    'bb' : BB_PATH,
    'bk' : BK_PATH,
    'bn' : BN_PATH,
    'bp' : BP_PATH,
    'bq' : BQ_PATH,
    'br' : BR_PATH,
    'wb' : WB_PATH,
    'wk' : WK_PATH,
    'wn' : WN_PATH,
    'wp' : WP_PATH,
    'wq' : WQ_PATH,
    'wr' : WR_PATH
}

LIGHT_SQUARE_COLOR = (235, 236, 208)
DARK_SQUARE_COLOR = (115, 149, 82)
SELECTED_LIGHT_SQUARE_COLOR = (245, 246, 130)
SELECTED_DARK_SQUARE_COLOR = (185, 202, 67)
PROMOTION_MENU_COLOR = (255, 255, 255)
LEGAL_MOVE_COLOR_MULTIPLIER = 0.86
BACKGROUND_COLOR = (68, 66, 63)
CLOCK_BLACK_COLOR = (38, 36, 33)
CLOCK_WHITE_COLOR = (255, 255, 255)


DEFAULT_WINDOW_WIDTH = 640
DEFAULT_WINDOW_HEIGHT = 640 * 9 / 8

DEFAULT_BOARD_WIDTH = 640
DEFAULT_BOARD_HEIGHT = 640
DEFAULT_BOARD_TOPLEFT = (0,0)

DEFAULT_FONT = "Segoe UI"

DEFAULT_FPS = 144

DEFAULT_SEARCH_DEPTH = 3

DEFAULT_TIME_CONTROL = "3+2"

STARTING_POSITION_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
TEST_FEN = '1r4kr/pp2RRpp/8/1P4B1/8/8/P4PPP/6K1 b - - 0 1'
TEST_FEN_MATE = '2r2r2/6kp/3p4/3P4/4Pp2/5P1P/PP1pq1P1/4R2K b - - 0 1'

DRAW_BY_INSUFFICIENT_MATERIAL = 101
DRAW_BY_THREEFOLD_REPETITION = 102
DRAW_BY_50_MOVE_RULE = 103
DRAW_BY_STALEMATE = 104
WHITE_VICTORY_BY_CHECKMATE = 105
BLACK_VICTORY_BY_CHECKMATE = 106
WHITE_VICTORY_BY_TIMEOUT = 107
BLACK_VICTORY_BY_TIMEOUT = 108
DRAW_BY_TIMEOUT_AGAINST_INSUFFICIENT_MATERIAL = 109

INF = 9999

LOCAL = 201
AS_HOST = 202
AS_CLIENT = 203
AGAINST_COMPUTER = 204