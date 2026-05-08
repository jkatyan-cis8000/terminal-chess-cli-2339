"""Console-based output renderer implementation."""

from ..interfaces import OutputProvider
from ..ui.renderer import render_board, render_game_info, render_move_history
from ..core import GameState


class ConsoleOutputRenderer(OutputProvider):
    """Output renderer that prints to console using renderer functions."""
    
    def display_board(self, state: GameState) -> None:
        """Display the current board state."""
        history = state.move_history.moves
        last_move = history[-1] if history else None
        board_str = render_board(state, last_move)
        print(board_str)
    
    def display_game_info(self, state: GameState, last_move: str | None) -> None:
        """Display game info like turn, check status, etc."""
        info_str = render_game_info(state, last_move)
        print(info_str)
    
    def display_message(self, message: str) -> None:
        """Display a message to the user."""
        print(message)
    
    def display_error(self, error: str) -> None:
        """Display an error message."""
        print(f"Error: {error}")
