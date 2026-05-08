"""Turn management service."""

from __future__ import annotations

from src.core import GameState, Move, Color, PieceType
from src.logic.rules import (
    apply_castling, apply_en_passant, apply_promotion,
    update_castling_rights, update_en_passant_target
)
from src.logic.validation import can_piece_move_to, _is_king_in_check
from src.logic.check import is_check, is_checkmate, is_stalemate
from typing import Optional, Tuple


class TurnService:
    """Service for managing turns and move execution."""
    
    def __init__(self, initial_state: GameState):
        self.game_state = initial_state
        self.promotion_piece: Optional[PieceType] = None
    
    def get_current_player(self) -> Color:
        """Get the color of the current player."""
        return self.game_state.current_turn
    
    def get_valid_moves(self) -> list[Move]:
        """Get all valid moves for the current player."""
        from src.logic.check import get_all_legal_moves
        return get_all_legal_moves(self.game_state, self.game_state.current_turn)
    
    def is_move_valid(self, move: Move) -> bool:
        """Check if a move is valid for the current player."""
        if move.piece.color != self.game_state.current_turn:
            return False
        return move in self.get_valid_moves()
    
    def is_check(self) -> bool:
        """Check if current player is in check."""
        return is_check(self.game_state, self.game_state.current_turn)
    
    def is_checkmate(self) -> bool:
        """Check if current player is in checkmate."""
        return is_checkmate(self.game_state, self.game_state.current_turn)
    
    def is_stalemate(self) -> bool:
        """Check if current player is in stalemate."""
        return is_stalemate(self.game_state, self.game_state.current_turn)
    
    def is_game_over(self) -> Tuple[bool, Optional[str]]:
        """Check if game is over. Returns (is_over, result)."""
        if self.is_checkmate():
            winner = self.game_state.current_turn.opposite()
            return True, f"Checkmate! {winner.name.title()} wins!"
        elif self.is_stalemate():
            return True, "Stalemate! The game is a draw."
        return False, None
    
    def make_move(self, move: Move, promotion_type: Optional[PieceType] = None) -> GameState:
        """Execute a move and update game state."""
        # Make a copy of the state
        new_state = self.game_state.copy()
        
        # Handle special moves
        if move.is_castling:
            new_state = apply_castling(new_state, move)
        elif move.is_en_passant:
            new_state = apply_en_passant(new_state, move)
        else:
            # Normal move
            new_state.board[move.from_square] = None
            new_state.board[move.to_square] = move.piece
        
        # Handle promotion
        if move.promotion_piece:
            new_state.board[move.to_square] = Piece(move.promotion_piece, move.piece.color)
        elif promotion_type:
            new_state.board[move.to_square] = Piece(promotion_type, move.piece.color)
        
        # Update castling rights
        new_state = update_castling_rights(new_state, move)
        
        # Update en passant target
        new_state = update_en_passant_target(new_state, move)
        
        # Switch turns
        new_state.current_turn = self.game_state.current_turn.opposite()
        
        # Add to move history
        new_state.move_history = new_state.move_history.add_move(move)
        
        self.game_state = new_state
        return new_state
    
    def requires_promotion(self, move: Move) -> bool:
        """Check if the move requires pawn promotion."""
        piece = move.piece
        if piece.piece_type != PieceType.PAWN:
            return False
        return (piece.color == Color.WHITE and move.to_square.rank == 8) or \
               (piece.color == Color.BLACK and move.to_square.rank == 1)
    
    def set_promotion(self, piece_type: PieceType) -> None:
        """Set the promotion piece type."""
        if piece_type not in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
            raise ValueError("Invalid promotion piece type")
        self.promotion_piece = piece_type
    
    def clear_promotion(self) -> None:
        """Clear the promotion piece type."""
        self.promotion_piece = None
