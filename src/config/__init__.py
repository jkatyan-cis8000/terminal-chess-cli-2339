"""Constants and configuration for the chess game."""

from __future__ import annotations

from src.core import Piece, PieceType, Color, Square, GameState, MoveHistory
from typing import Literal


# Board dimensions
BOARD_SIZE = 8
FILES = ("a", "b", "c", "d", "e", "f", "g", "h")
RANKS = (1, 2, 3, 4, 5, 6, 7, 8)

# Piece values for evaluation
PIECE_VALUES = {
    PieceType.PAWN: 100,
    PieceType.KNIGHT: 320,
    PieceType.BISHOP: 330,
    PieceType.ROOK: 500,
    PieceType.QUEEN: 900,
    PieceType.KING: 20000,
}

# Initial board setup
INITIAL_BOARD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def create_initial_board() -> dict[Square, Piece]:
    """Create the initial board state."""
    board: dict[Square, Piece] = {}
    
    # Black pieces (rank 1 and 2)
    back_rank = [
        PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
        PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
    ]
    
    for file_idx, file in enumerate(FILES):
        board[Square(file=file, rank=1)] = Piece(PieceType.ROOK, Color.BLACK)
        board[Square(file=file, rank=2)] = Piece(PieceType.PAWN, Color.BLACK)
    
    # White pieces (rank 7 and 8)
    for file_idx, file in enumerate(FILES):
        board[Square(file=file, rank=7)] = Piece(PieceType.PAWN, Color.WHITE)
        board[Square(file=file, rank=8)] = Piece(back_rank[file_idx], Color.WHITE)
    
    return board


def create_initial_game_state() -> GameState:
    """Create the initial game state."""
    return GameState(
        board=create_initial_board(),
        current_turn=Color.WHITE,
        castling_rights={
            Color.WHITE: {
                "kingside": True,
                "queenside": True,
            },
            Color.BLACK: {
                "kingside": True,
                "queenside": True,
            },
        },
        en_passant_target=None,
        move_history=MoveHistory(()),
    )


# Piece symbols for display (Unicode)
PIECE_SYMBOLS = {
    (PieceType.PAWN, Color.WHITE): "♙",
    (PieceType.PAWN, Color.BLACK): "♟",
    (PieceType.ROOK, Color.WHITE): "♖",
    (PieceType.ROOK, Color.BLACK): "♜",
    (PieceType.KNIGHT, Color.WHITE): "♘",
    (PieceType.KNIGHT, Color.BLACK): "♞",
    (PieceType.BISHOP, Color.WHITE): "♗",
    (PieceType.BISHOP, Color.BLACK): "♝",
    (PieceType.QUEEN, Color.WHITE): "♕",
    (PieceType.QUEEN, Color.BLACK): "♛",
    (PieceType.KING, Color.WHITE): "♔",
    (PieceType.KING, Color.BLACK): "♚",
}

# Terminal display constants
TERMINAL_COLORS = {
    "white": "\033[97m",
    "black": "\033[90m",
    "highlight": "\033[43m",
    "reset": "\033[0m",
}
