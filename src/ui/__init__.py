"""User-facing interface: CLI rendering and parsing.

The UI layer depends on lower layers (types, config, service, runtime, providers)
and provides user-facing surfaces like CLI rendering and input parsing.
"""

from .renderer import (
    render_board,
    render_game_info,
    render_move_history,
    render_promotion_prompt,
    render_error,
    render_success,
    format_move_notation,
)
from .parser import InputParser
from .input_handler import ConsoleInputHandler
from .output_renderer import ConsoleOutputRenderer

__all__ = [
    "render_board",
    "render_game_info",
    "render_move_history",
    "render_promotion_prompt",
    "render_error",
    "render_success",
    "format_move_notation",
    "InputParser",
    "ConsoleInputHandler",
    "ConsoleOutputRenderer",
]
