"""Chess piece and game types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal, NewType, Optional


class Color(Enum):
    """Piece color."""
    WHITE = "white"
    BLACK = "black"

    def opposite(self) -> Color:
        """Return the opposite color."""
        return Color.BLACK if self == Color.WHITE else Color.WHITE


class PieceType(Enum):
    """Piece types."""
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"


@dataclass(frozen=True)
class Piece:
    """A chess piece."""
    piece_type: PieceType
    color: Color

    def __str__(self) -> str:
        return f"{self.color.name[0]}{self.piece_type.value[0].upper()}"


@dataclass(frozen=True)
class Square:
    """A chess square (file, rank)."""
    file: Literal["a", "b", "c", "d", "e", "f", "g", "h"]
    rank: Literal[1, 2, 3, 4, 5, 6, 7, 8]

    def __str__(self) -> str:
        return f"{self.file}{self.rank}"

    @classmethod
    def from_algebraic(cls, algebraic: str) -> Optional[Square]:
        """Parse a square from algebraic notation (e.g., 'e4')."""
        if len(algebraic) != 2:
            return None
        file = algebraic[0]
        rank_str = algebraic[1]
        
        if file not in "abcdefgh":
            return None
        if rank_str not in "12345678":
            return None
        
        return cls(file=file, rank=int(rank_str))

    def to_algebraic(self) -> str:
        """Convert square to algebraic notation."""
        return f"{self.file}{self.rank}"


class Rank(Enum):
    """Rank enumeration for pawn promotion."""
    RANK_1 = 1
    RANK_2 = 2
    RANK_3 = 3
    RANK_4 = 4
    RANK_5 = 5
    RANK_6 = 6
    RANK_7 = 7
    RANK_8 = 8


class File(Enum):
    """File enumeration."""
    FILE_A = "a"
    FILE_B = "b"
    FILE_C = "c"
    FILE_D = "d"
    FILE_E = "e"
    FILE_F = "f"
    FILE_G = "g"
    FILE_H = "h"


@dataclass(frozen=True)
class Move:
    """A chess move."""
    from_square: Square
    to_square: Square
    piece: Piece
    captured_piece: Optional[Piece] = None
    is_castling: bool = False
    is_en_passant: bool = False
    promotion_piece: Optional[PieceType] = None

    def __str__(self) -> str:
        base = f"{self.piece.piece_type.value[0].upper()}{self.from_square}{self.to_square}"
        if self.is_castling:
            if self.to_square.file == "g":
                base = "O-O"
            else:
                base = "O-O-O"
        return base


@dataclass(frozen=True)
class MoveHistory:
    """Complete move history for the game."""
    moves: tuple[Move, ...]

    def add_move(self, move: Move) -> MoveHistory:
        """Add a move and return new history."""
        return MoveHistory(self.moves + (move,))

    def last_move(self) -> Optional[Move]:
        """Get the last move, if any."""
        if not self.moves:
            return None
        return self.moves[-1]


@dataclass
class GameState:
    """Current game state."""
    board: dict[Square, Piece]
    current_turn: Color
    castling_rights: dict[Color, dict[str, bool]]
    en_passant_target: Optional[Square] = None
    move_history: MoveHistory = MoveHistory(())

    def copy(self) -> GameState:
        """Create a copy of the game state."""
        return GameState(
            board=dict(self.board),
            current_turn=self.current_turn,
            castling_rights={
                color: dict(castling)
                for color, castling in self.castling_rights.items()
            },
            en_passant_target=self.en_passant_target,
            move_history=self.move_history,
        )


# Type aliases for clarity
Position = NewType("Position", Square)
BoardState = NewType("BoardState", dict[Square, Piece])
