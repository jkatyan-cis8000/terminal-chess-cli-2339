"""Castling, en passant, and promotion rules."""

from __future__ import annotations

from ..core import GameState, Move, Piece, PieceType, Square, Color
from ..config import RANKS
from ..logic.validation import _is_king_in_check, _is_square_attacked
from typing import Optional


def can_perform_castling(game_state: GameState, move: Move) -> bool:
    """Check if castling is allowed."""
    if not move.is_castling:
        return False
    
    piece = game_state.board.get(move.from_square)
    if piece is None or piece.piece_type != PieceType.KING:
        return False
    
    color = piece.color
    castling_rights = game_state.castling_rights[color]
    
    # Determine which side
    if move.to_square.file == "g":  # Kingside
        if not castling_rights["kingside"]:
            return False
        # Check path is clear
        for sq_file in ("f", "g"):
            if game_state.board.get(Square(file=sq_file, rank=move.from_square.rank)) is not None:
                return False
    elif move.to_square.file == "c":  # Queenside
        if not castling_rights["queenside"]:
            return False
        # Check path is clear
        for sq_file in ("b", "c", "d"):
            if game_state.board.get(Square(file=sq_file, rank=move.from_square.rank)) is not None:
                return False
    else:
        return False
    
    # King must not be in check
    if _is_king_in_check(game_state, color):
        return False
    
    # King must not pass through check
    king_rank = move.from_square.rank
    for sq_file in ("f", "g") if move.to_square.file == "g" else ("c", "d"):
        if _is_square_attacked(game_state, Square(file=sq_file, rank=king_rank), color.opposite()):
            return False
    
    return True


def can_perform_en_passant(game_state: GameState, move: Move) -> bool:
    """Check if en passant capture is allowed."""
    if not move.is_en_passant:
        return False
    
    piece = game_state.board.get(move.from_square)
    if piece is None or piece.piece_type != PieceType.PAWN:
        return False
    
    # Check if en passant target is set and matches destination
    if game_state.en_passant_target != move.to_square:
        return False
    
    return True


def can_perform_promotion(game_state: GameState, move: Move, promotion_type: PieceType) -> bool:
    """Check if pawn promotion is allowed."""
    piece = game_state.board.get(move.from_square)
    if piece is None or piece.piece_type != PieceType.PAWN:
        return False
    
    # Check if pawn has reached promotion rank
    if piece.color == Color.WHITE and move.to_square.rank != 8:
        return False
    if piece.color == Color.BLACK and move.to_square.rank != 1:
        return False
    
    # Validate promotion piece type
    if promotion_type not in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
        return False
    
    return True


def apply_castling(game_state: GameState, move: Move) -> GameState:
    """Apply castling move to the game state."""
    new_state = game_state.copy()
    color = move.piece.color
    
    # Move king
    new_state.board[move.from_square] = None
    new_state.board[move.to_square] = move.piece
    
    # Determine castling side
    if move.to_square.file == "g":  # Kingside
        rook_from = Square(file="h", rank=move.from_square.rank)
        rook_to = Square(file="f", rank=move.from_square.rank)
    elif move.to_square.file == "c":  # Queenside
        rook_from = Square(file="a", rank=move.from_square.rank)
        rook_to = Square(file="d", rank=move.from_square.rank)
    else:
        return new_state
    
    # Move rook
    rook = new_state.board[rook_from]
    if rook is not None:
        new_state.board[rook_from] = None
        new_state.board[rook_to] = rook
    
    # Update castling rights
    new_state.castling_rights[color]["kingside"] = False
    new_state.castling_rights[color]["queenside"] = False
    
    return new_state


def apply_en_passant(game_state: GameState, move: Move) -> GameState:
    """Apply en passant capture to the game state."""
    new_state = game_state.copy()
    
    # Move pawn
    new_state.board[move.from_square] = None
    new_state.board[move.to_square] = move.piece
    
    # Remove captured pawn (behind the moving pawn)
    capture_rank = move.from_square.rank
    capture_sq = Square(file=move.to_square.file, rank=capture_rank)
    new_state.board[capture_sq] = None
    
    return new_state


def apply_promotion(game_state: GameState, move: Move, promotion_type: PieceType) -> GameState:
    """Apply pawn promotion to the game state."""
    new_state = game_state.copy()
    
    # Move pawn
    new_state.board[move.from_square] = None
    
    # Place promoted piece
    promoted_piece = Piece(promotion_type, move.piece.color)
    new_state.board[move.to_square] = promoted_piece
    
    return new_state


def update_castling_rights(game_state: GameState, move: Move) -> GameState:
    """Update castling rights after a move."""
    new_state = game_state.copy()
    piece = move.piece
    
    # King moves - lose both castling rights
    if piece.piece_type == PieceType.KING:
        new_state.castling_rights[piece.color]["kingside"] = False
        new_state.castling_rights[piece.color]["queenside"] = False
    
    # Rook moves or captures - lose that side's castling rights
    if piece.piece_type == PieceType.ROOK:
        if move.from_square.file == "a" and move.from_square.rank == 1:
            new_state.castling_rights[Color.WHITE]["queenside"] = False
        elif move.from_square.file == "h" and move.from_square.rank == 1:
            new_state.castling_rights[Color.WHITE]["kingside"] = False
        elif move.from_square.file == "a" and move.from_square.rank == 8:
            new_state.castling_rights[Color.BLACK]["queenside"] = False
        elif move.from_square.file == "h" and move.from_square.rank == 8:
            new_state.castling_rights[Color.BLACK]["kingside"] = False
    
    return new_state


def update_en_passant_target(game_state: GameState, move: Move) -> GameState:
    """Update en passant target square after a move."""
    new_state = game_state.copy()
    
    piece = move.piece
    if piece.piece_type == PieceType.PAWN:
        # Two-square pawn move creates en passant target
        if abs(move.to_square.rank - move.from_square.rank) == 2:
            # Target is the square the pawn skipped over
            mid_rank = (move.from_square.rank + move.to_square.rank) // 2
            new_state.en_passant_target = Square(
                file=move.from_square.file,
                rank=mid_rank
            )
        else:
            new_state.en_passant_target = None
    else:
        new_state.en_passant_target = None
    
    return new_state
