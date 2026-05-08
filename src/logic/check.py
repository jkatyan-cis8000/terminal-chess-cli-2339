"""Check and checkmate detection."""

from __future__ import annotations

from ..core import GameState, Move, Piece, PieceType, Square, Color
from ..logic.validation import _is_square_attacked


def get_all_moves(game_state: GameState, color: Color) -> list[Move]:
    """Get all legal moves for a given color."""
    from ..logic.validation import can_piece_move_to
    
    moves = []
    for from_sq, piece in game_state.board.items():
        if piece.color != color:
            continue
        
        # Try all possible destination squares
        for file in "abcdefgh":
            for rank in range(1, 9):
                to_sq = Square(file=file, rank=rank)
                
                move = Move(
                    from_square=from_sq,
                    to_square=to_sq,
                    piece=piece
                )
                
                if can_piece_move_to(game_state, move):
                    moves.append(move)
    
    return moves


def is_check(game_state: GameState, color: Color) -> bool:
    """Check if the king of the given color is in check."""
    # Find the king
    king_sq = None
    for sq, piece in game_state.board.items():
        if piece.piece_type == PieceType.KING and piece.color == color:
            king_sq = sq
            break
    
    if king_sq is None:
        return False
    
    # Check if any opponent piece can attack the king
    return _is_square_attacked(game_state, king_sq, color.opposite())


def get_king_square(game_state: GameState, color: Color) -> Square | None:
    """Get the king's square for the given color."""
    for sq, piece in game_state.board.items():
        if piece.piece_type == PieceType.KING and piece.color == color:
            return sq
    return None


def is_checkmate(game_state: GameState, color: Color) -> bool:
    """Check if the given color is in checkmate."""
    if not is_check(game_state, color):
        return False
    
    # Check if any legal move can get the king out of check
    return not has_legal_moves(game_state, color)


def is_stalemate(game_state: GameState, color: Color) -> bool:
    """Check if the given color is in stalemate."""
    if is_check(game_state, color):
        return False
    
    # Check if player has any legal moves
    return not has_legal_moves(game_state, color)


def has_legal_moves(game_state: GameState, color: Color) -> bool:
    """Check if the given color has any legal moves."""
    from ..logic.validation import can_piece_move_to
    
    # Get all pieces for this color
    for from_sq, piece in game_state.board.items():
        if piece.color != color:
            continue
        
        # Try all possible destination squares
        for file in "abcdefgh":
            for rank in range(1, 9):
                to_sq = Square(file=file, rank=rank)
                
                move = Move(
                    from_square=from_sq,
                    to_square=to_sq,
                    piece=piece
                )
                
                if can_piece_move_to(game_state, move):
                    # Check if this move would leave king in check
                    if not would_leave_king_in_check(game_state, move):
                        return True
    
    return False


def would_leave_king_in_check(game_state: GameState, move: Move) -> bool:
    """Check if making a move would leave the moving player's king in check."""
    # Make the move on a copy
    temp_state = game_state.copy()
    
    # Apply the move
    temp_state.board[move.from_square] = None
    temp_state.board[move.to_square] = move.piece
    
    # Check if king is in check after the move
    return is_check(temp_state, move.piece.color)


def get_all_legal_moves(game_state: GameState, color: Color) -> list[Move]:
    """Get all legal moves for a given color (filters out self-check)."""
    from ..logic.validation import can_piece_move_to
    
    all_moves = get_all_moves(game_state, color)
    legal_moves = []
    
    for move in all_moves:
        if not would_leave_king_in_check(game_state, move):
            legal_moves.append(move)
    
    return legal_moves
