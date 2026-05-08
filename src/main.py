"""Main entry point for the chess game."""

from __future__ import annotations

from src.core import GameState, Color
from src.config import create_initial_board
from src.controller.game import GameRuntime
from src.ui.input_handler import ConsoleInputHandler
from src.ui.output_renderer import ConsoleOutputRenderer


def create_initial_state() -> GameState:
    """Create the initial game state."""
    from src.core import GameState, MoveHistory
    from src.persistence import BoardRepository
    
    # Initialize board
    board = create_initial_board()
    repo = BoardRepository()
    repo.set_board(board)
    
    # Create initial game state
    state = GameState(
        board=board,
        current_turn=Color.WHITE,
        castling_rights={
            Color.WHITE: {"kingside": True, "queenside": True},
            Color.BLACK: {"kingside": True, "queenside": True}
        },
        en_passant_target=None,
        move_history=MoveHistory(())
    )
    
    return state


def main() -> None:
    """Main entry point."""
    # Create initial state
    initial_state = create_initial_state()
    
    # Create UI providers
    input_provider = ConsoleInputHandler(initial_state)
    output_provider = ConsoleOutputRenderer()
    
    # Create and run game with providers injected
    game = GameRuntime(initial_state, input_provider, output_provider)
    game.run()


if __name__ == "__main__":
    main()
