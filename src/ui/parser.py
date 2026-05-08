"""Input parsing for algebraic notation."""

from __future__ import annotations

import re
from ..core import Move, Piece, PieceType, Square, Color, GameState
from ..config import PIECE_SYMBOLS
from typing import Optional


class InputParser:
    """Parser for chess move input in algebraic notation."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def parse(self, input_str: str) -> Optional[Move]:
        """Parse user input into a Move object."""
        input_str = input_str.strip().lower()
        
        if not input_str:
            return None
        
        # Handle castling
        if input_str in ("o-o", "castle kingside", "kingside"):
            return self._parse_castling("kingside")
        elif input_str in ("o-o-o", "castle queenside", "queenside"):
            return self._parse_castling("queenside")
        
        # Handle standard notation (e.g., "e2e4", "Ke8", "Nf3", "exd5")
        return self._parse_standard_notation(input_str)
    
    def _parse_castling(self, side: str) -> Optional[Move]:
        """Parse castling move."""
        color = self.game_state.current_turn
        rank = 1 if color == Color.WHITE else 8
        
        if side == "kingside":
            from_sq = Square(file="e", rank=rank)
            to_sq = Square(file="g", rank=rank)
        else:  # queenside
            from_sq = Square(file="e", rank=rank)
            to_sq = Square(file="c", rank=rank)
        
        piece = self.game_state.board.get(from_sq)
        if piece is None:
            return None
        
        move = Move(
            from_square=from_sq,
            to_square=to_sq,
            piece=piece,
            is_castling=True
        )
        
        return move
    
    def _parse_standard_notation(self, input_str: str) -> Optional[Move]:
        """Parse standard algebraic notation."""
        # Pattern: [piece][from_file][from_rank][x][to_file][to_rank]
        # Examples: e2e4, Ke8, Nf3, exd5, O-O
        
        # First, try simple format: e2e4
        if len(input_str) == 4 and re.match(r"[a-h][1-8][a-h][1-8]", input_str):
            return self._parse_simple_notation(input_str)
        
        # Try longer format with piece: Ke8, Nf3
        if len(input_str) >= 3:
            return self._parse_full_notation(input_str)
        
        return None
    
    def _parse_simple_notation(self, input_str: str) -> Optional[Move]:
        """Parse simple format: e2e4"""
        from_file = input_str[0]
        from_rank = int(input_str[1])
        to_file = input_str[2]
        to_rank = int(input_str[3])
        
        from_sq = Square(file=from_file, rank=from_rank)
        to_sq = Square(file=to_file, rank=to_rank)
        
        piece = self.game_state.board.get(from_sq)
        if piece is None:
            return None
        
        is_capture = self.game_state.board.get(to_sq) is not None
        
        move = Move(
            from_square=from_sq,
            to_square=to_sq,
            piece=piece,
            is_capture=is_capture
        )
        
        return move
    
    def _parse_full_notation(self, input_str: str) -> Optional[Move]:
        """Parse full notation: Ke8, Nf3, exd5"""
        color = self.game_state.current_turn
        
        # Extract piece type
        piece_type = None
        rest = input_str
        
        if input_str[0].isupper():
            piece_char = input_str[0].lower()
            piece_types = {
                'k': PieceType.KING,
                'q': PieceType.QUEEN,
                'r': PieceType.ROOK,
                'b': PieceType.BISHOP,
                'n': PieceType.KNIGHT
            }
            piece_type = piece_types.get(piece_char)
            rest = input_str[1:]
        
        # Extract capture marker
        is_capture = 'x' in rest
        rest = rest.replace('x', '')
        
        # Extract to square
        if len(rest) >= 2:
            to_file = rest[-2]
            to_rank = int(rest[-1])
            to_sq = Square(file=to_file, rank=to_rank)
            rest = rest[:-2]
        else:
            return None
        
        # Extract from square info (file/rank)
        from_file = None
        from_rank = None
        
        for char in rest:
            if char in "abcdefgh":
                from_file = char
            elif char.isdigit():
                from_rank = int(char)
        
        # Find matching piece
        for sq, piece in self.game_state.board.items():
            if piece.color != color:
                continue
            if piece_type and piece.piece_type != piece_type:
                continue
            if from_file and sq.file != from_file:
                continue
            if from_rank and sq.rank != from_rank:
                continue
            
            # Check if this piece can move to the target
            move = Move(
                from_square=sq,
                to_square=to_sq,
                piece=piece,
                is_capture=is_capture
            )
            
            if self._validate_move(move):
                return move
        
        return None
    
    def _validate_move(self, move: Move) -> bool:
        """Check if a move is valid."""
        # Check if piece can move to destination
        piece = move.piece
        if piece is None:
            return False
        
        # Get all valid moves for this piece
        from ..logic.validation import can_piece_move_to
        
        return can_piece_move_to(self.game_state, move)
