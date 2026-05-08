"""Move validation logic."""

from __future__ import annotations

from ..core import GameState, Move, Piece, PieceType, Square, Color
from ..config import FILES, RANKS
from typing import Optional


def is_valid_square(square: Square) -> bool:
    """Check if a square is within board bounds."""
    return square.file in FILES and square.rank in RANKS


def is_same_square(sq1: Square, sq2: Square) -> bool:
    """Check if two squares are the same."""
    return sq1.file == sq2.file and sq1.rank == sq2.rank


def get_square_diff(sq1: Square, sq2: Square) -> tuple[int, int]:
    """Get the difference in file and rank between two squares."""
    file_diff = ord(sq2.file) - ord(sq1.file)
    rank_diff = sq2.rank - sq1.rank
    return file_diff, rank_diff


def is_path_clear(game_state: GameState, from_sq: Square, to_sq: Square) -> bool:
    """Check if the path between two squares is clear (no pieces in between)."""
    from ..persistence import BoardRepository
    
    repo = BoardRepository()
    repo.set_board(game_state.board)
    
    file_diff, rank_diff = get_square_diff(from_sq, to_sq)
    
    # Determine direction of movement
    file_step = 0 if file_diff == 0 else (1 if file_diff > 0 else -1)
    rank_step = 0 if rank_diff == 0 else (1 if rank_diff > 0 else -1)
    
    current_file = from_sq.file
    current_rank = from_sq.rank
    
    # Check all squares between from and to (excluding both endpoints)
    while True:
        current_file = chr(ord(current_file) + file_step)
        current_rank += rank_step
        
        if current_file == to_sq.file and current_rank == to_sq.rank:
            break
        
        current_sq = Square(file=current_file, rank=current_rank)
        if repo.get_piece(current_sq) is not None:
            return False
    
    return True


def can_piece_move_to(game_state: GameState, move: Move) -> bool:
    """Check if the piece can legally move to the destination."""
    piece = game_state.board.get(move.from_square)
    if piece is None:
        return False
    
    # Can't move to same square
    if is_same_square(move.from_square, move.to_square):
        return False
    
    # Can't capture own piece
    target_piece = game_state.board.get(move.to_square)
    if target_piece is not None and target_piece.color == piece.color:
        return False
    
    file_diff, rank_diff = get_square_diff(move.from_square, move.to_square)
    
    # Validate movement based on piece type
    if piece.piece_type == PieceType.PAWN:
        return _validate_pawn_move(game_state, move, file_diff, rank_diff)
    elif piece.piece_type == PieceType.ROOK:
        return _validate_rook_move(file_diff, rank_diff)
    elif piece.piece_type == PieceType.KNIGHT:
        return _validate_knight_move(file_diff, rank_diff)
    elif piece.piece_type == PieceType.BISHOP:
        return _validate_bishop_move(file_diff, rank_diff)
    elif piece.piece_type == PieceType.QUEEN:
        return _validate_queen_move(file_diff, rank_diff)
    elif piece.piece_type == PieceType.KING:
        return _validate_king_move(game_state, move, file_diff, rank_diff)
    
    return False


def _validate_pawn_move(
    game_state: GameState,
    move: Move,
    file_diff: int,
    rank_diff: int
) -> bool:
    """Validate pawn movement."""
    piece = game_state.board[move.from_square]
    direction = 1 if piece.color == Color.WHITE else -1
    
    # Forward move (one square)
    if file_diff == 0 and rank_diff == direction:
        return game_state.board.get(move.to_square) is None
    
    # Forward move (two squares) - only from starting position
    if file_diff == 0 and rank_diff == 2 * direction:
        start_rank = 2 if piece.color == Color.WHITE else 7
        if move.from_square.rank != start_rank:
            return False
        if game_state.board.get(move.to_square) is not None:
            return False
        intermediate_sq = Square(
            file=move.from_square.file,
            rank=move.from_square.rank + direction
        )
        return game_state.board.get(intermediate_sq) is None
    
    # Diagonal capture
    if abs(file_diff) == 1 and rank_diff == direction:
        # Normal capture
        target_piece = game_state.board.get(move.to_square)
        if target_piece is not None and target_piece.color != piece.color:
            return True
        # En passant capture
        if move.to_square == game_state.en_passant_target:
            return True
    
    return False


def _validate_rook_move(file_diff: int, rank_diff: int) -> bool:
    """Validate rook movement (straight lines)."""
    return file_diff == 0 or rank_diff == 0


def _validate_knight_move(file_diff: int, rank_diff: int) -> bool:
    """Validate knight movement (L-shape)."""
    abs_file = abs(file_diff)
    abs_rank = abs(rank_diff)
    return (abs_file == 2 and abs_rank == 1) or (abs_file == 1 and abs_rank == 2)


def _validate_bishop_move(file_diff: int, rank_diff: int) -> bool:
    """Validate bishop movement (diagonals)."""
    return abs(file_diff) == abs(rank_diff)


def _validate_queen_move(file_diff: int, rank_diff: int) -> bool:
    """Validate queen movement (straight or diagonal)."""
    return file_diff == 0 or rank_diff == 0 or abs(file_diff) == abs(rank_diff)


def _validate_king_move(
    game_state: GameState,
    move: Move,
    file_diff: int,
    rank_diff: int
) -> bool:
    """Validate king movement (one square in any direction) or castling."""
    # Normal king move
    if abs(file_diff) <= 1 and abs(rank_diff) <= 1:
        return True
    
    # Castling move
    if rank_diff == 0 and abs(file_diff) == 2:
        return _validate_castling(game_state, move)
    
    return False


def _validate_castling(game_state: GameState, move: Move) -> bool:
    """Validate castling move."""
    piece = game_state.board[move.from_square]
    if piece.piece_type != PieceType.KING:
        return False
    
    color = piece.color
    castling_rights = game_state.castling_rights[color]
    
    # King must not have moved
    if not castling_rights["kingside"] and not castling_rights["queenside"]:
        return False
    
    # Check which side is being castled
    if move.to_square.file == "g":  # Kingside
        # King-side castling rights
        if not castling_rights["kingside"]:
            return False
        # Path must be clear
        rook_sq = Square(file="h", rank=move.from_square.rank)
        if game_state.board.get(rook_sq) is None:
            return False
        if game_state.board.get(rook_sq).piece_type != PieceType.ROOK:
            return False
        # Squares between king and rook must be empty
        for sq_file in ("f", "g"):
            if game_state.board.get(Square(file=sq_file, rank=move.from_square.rank)) is not None:
                return False
        # King must not be in check and must not pass through check
        if _is_king_in_check(game_state, color):
            return False
        # King's path must not be under attack
        for sq_file in ("f", "g"):
            if _is_square_attacked(game_state, Square(file=sq_file, rank=move.from_square.rank), color.opposite()):
                return False
    elif move.to_square.file == "c":  # Queenside
        # Queen-side castling rights
        if not castling_rights["queenside"]:
            return False
        # Path must be clear
        rook_sq = Square(file="a", rank=move.from_square.rank)
        if game_state.board.get(rook_sq) is None:
            return False
        if game_state.board.get(rook_sq).piece_type != PieceType.ROOK:
            return False
        # Squares between king and rook must be empty
        for sq_file in ("b", "c", "d"):
            if game_state.board.get(Square(file=sq_file, rank=move.from_square.rank)) is not None:
                return False
        # King must not be in check and must not pass through check
        if _is_king_in_check(game_state, color):
            return False
        # King's path must not be under attack
        for sq_file in ("c", "d"):
            if _is_square_attacked(game_state, Square(file=sq_file, rank=move.from_square.rank), color.opposite()):
                return False
    else:
        return False
    
    return True


def _is_king_in_check(game_state: GameState, color: Color) -> bool:
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


def _is_square_attacked(game_state: GameState, square: Square, attacker_color: Color) -> bool:
    """Check if a square is attacked by any piece of the given color."""
    # Create a temporary game state to check attacks
    temp_state = game_state.copy()
    
    # Check all opponent pieces
    for sq, piece in game_state.board.items():
        if piece.color != attacker_color:
            continue
        
        # Try a move from this piece to the square
        move = Move(
            from_square=sq,
            to_square=square,
            piece=piece
        )
        
        # Check if this move is legal for the piece
        if can_piece_move_to(game_state, move):
            return True
    
    return False
