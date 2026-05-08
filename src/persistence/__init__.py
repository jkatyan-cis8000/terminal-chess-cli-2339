"""Board repository - stores and retrieves board state."""

from __future__ import annotations

from src.core import GameState, Move, Piece, Square
from typing import Optional


class BoardRepository:
    """
    Repository for board state persistence.
    Provides methods to get/set board state.
    """
    
    def __init__(self) -> None:
        self._board: dict[Square, Piece] = {}
    
    def set_board(self, board: dict[Square, Piece]) -> None:
        """Set the current board state."""
        self._board = dict(board)
    
    def get_board(self) -> dict[Square, Piece]:
        """Get the current board state."""
        return dict(self._board)
    
    def get_piece(self, square: Square) -> Optional[Piece]:
        """Get the piece at a given square."""
        return self._board.get(square)
    
    def set_piece(self, square: Square, piece: Optional[Piece]) -> None:
        """Set a piece at a given square (None to remove)."""
        if piece is None:
            self._board.pop(square, None)
        else:
            self._board[square] = piece
    
    def update_move(self, move: Move) -> None:
        """Update board state after a move."""
        # Remove piece from source square
        self._board.pop(move.from_square, None)
        
        # Place piece at destination square
        # For pawn promotion, use the promotion piece type
        piece_to_place = move.piece
        if move.promotion_piece:
            piece_to_place = Piece(move.promotion_piece, move.piece.color)
        
        self._board[move.to_square] = piece_to_place
        
        # Handle en passant capture
        if move.is_en_passant:
            # Remove the captured pawn
            capture_square = Square(
                file=move.to_square.file,
                rank=move.from_square.rank
            )
            self._board.pop(capture_square, None)
    
    def copy(self) -> BoardRepository:
        """Create a copy of this repository."""
        new_repo = BoardRepository()
        new_repo._board = dict(self._board)
        return new_repo
