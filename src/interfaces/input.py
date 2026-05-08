"""Input provider interface for chess game."""

from typing import Protocol

from src.core import Move


class InputProvider(Protocol):
    """Interface for getting user input."""

    def get_user_input(self) -> str: ...

    def parse_move(self, input_str: str) -> Move | None: ...

    def get_promotion_choice(self) -> str: ...
