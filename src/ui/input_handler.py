"""Console-based input handler implementation."""

from ..interfaces import InputProvider
from ..ui.parser import InputParser
from ..core import GameState, Move


class ConsoleInputHandler(InputProvider):
    """Input handler that reads from console and parses using InputParser."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.parser = InputParser(game_state)
    
    def get_user_input(self) -> str:
        """Get raw user input from stdin."""
        return input("Enter your move: ")
    
    def parse_move(self, input_str: str) -> Move | None:
        """Parse user input into a Move, or None if invalid."""
        return self.parser.parse(input_str)
    
    def get_promotion_choice(self) -> str:
        """Get promotion piece choice from user."""
        return input("Choose promotion (q/r/b/n): ").strip().lower()
