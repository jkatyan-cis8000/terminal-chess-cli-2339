"""Board display rendering."""

from __future__ import annotations

from ..core import GameState, Move, Color, PieceType
from ..config import PIECE_SYMBOLS


def render_board(game_state: GameState, last_move: Move | None = None) -> str:
    """Render the current board state for terminal display."""
    lines = []
    
    # Header
    lines.append("")
    lines.append("  a b c d e f g h")
    lines.append(" +-----------------+")
    
    # Board rows (rank 8 to rank 1)
    for rank in range(8, 0, -1):
        row = f"{rank}|"
        for file in "abcdefgh":
            sq = f"{file}{rank}"
            piece = game_state.board.get(sq)
            
            # Highlight last move
            if last_move and (sq == last_move.from_square or sq == last_move.to_square):
                row += "✓"
            elif piece is None:
                row += " "
            else:
                symbol = PIECE_SYMBOLS[piece.piece_type][piece.color]
                row += symbol
            row += "|"
        
        lines.append(row)
        lines.append(" +-----------------+")
    
    lines.append("  a b c d e f h")
    lines.append("")
    
    return "\n".join(lines)


def render_game_info(game_state: GameState, last_move: Move | None = None) -> str:
    """Render game status and turn information."""
    lines = []
    
    # Current turn
    turn_str = game_state.current_turn.name.title()
    lines.append(f"Turn: {turn_str}")
    
    # Check status
    from ..logic.check import is_check
    if is_check(game_state, game_state.current_turn):
        lines.append("Status: CHECK!")
    
    # Last move
    if last_move:
        notation = format_move_notation(last_move)
        lines.append(f"Last move: {notation}")
    
    lines.append("")
    return "\n".join(lines)


def format_move_notation(move: Move) -> str:
    """Format a move as standard algebraic notation."""
    piece = move.piece
    from_sq = move.from_square
    to_sq = move.to_square
    
    # Castling
    if move.is_castling:
        if to_sq.file == "g":  # Kingside
            return "O-O"
        else:  # Queenside
            return "O-O-O"
    
    # En passant
    if move.is_en_passant:
        return f"{from_sq.file}x{to_sq}"
    
    # Pawn move
    if piece.piece_type == PieceType.PAWN:
        if move.is_capture:
            return f"{from_sq.file}x{to_sq}"
        else:
            return to_sq
    
    # Piece move
    piece_char = piece.piece_type.name[0]
    capture_str = "x" if move.is_capture else ""
    return f"{piece_char}{capture_str}{to_sq}"


def render_move_history(game_state: GameState, max_moves: int = 10) -> str:
    """Render recent move history."""
    history = game_state.move_history.moves
    
    if not history:
        return "No moves yet."
    
    lines = []
    # Show last max_moves moves
    for i, move in enumerate(history[-max_moves:], start=max(1, len(history) - max_moves + 1)):
        turn_num = (i + 1) // 2
        move_num = (i % 2) + 1
        
        if move_num == 1:
            lines.append(f"{turn_num}. {format_move_notation(move)}")
        else:
            lines[-1] += f"   {format_move_notation(move)}"
    
    return "\n".join(lines)


def render_promotion_prompt(color: Color) -> str:
    """Render promotion choice prompt."""
    return f"""
{color.name.title()} to promote:
1. Queen  (Q)
2. Rook   (R)
3. Bishop (B)
4. Knight (N)

Enter choice: """


def render_error(message: str) -> str:
    """Render error message."""
    return f"Error: {message}\n"


def render_success(message: str) -> str:
    """Render success message."""
    return f"{message}\n"
