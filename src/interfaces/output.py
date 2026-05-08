"""Output provider interface for chess game."""

from typing import Protocol

from src.core import GameState


class OutputProvider(Protocol):
    """Interface for displaying output to user."""

    def display_board(self, state: GameState) -> None: ...

    def display_game_info(self, state: GameState, last_move: str | None) -> None: ...

    def display_message(self, message: str) -> None: ...

    def display_error(self, error: str) -> None: ...

    def display_game_info(self, state: GameState) -> None:
        """Display game info like turn, check status, etc."""
        ...

    def display_message(self, message: str) -> None:
        """Display a message to the user."""
        ...

    def display_error(self, error: str) -> None:
        """Display an error message."""
        ...
