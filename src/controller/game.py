"""Runtime service for game orchestration."""

from __future__ import annotations

from src.core import GameState, Move, Color, PieceType
from src.logic.turn import TurnService
from typing import Optional
from src.persistence import BoardRepository
from src.interfaces import InputProvider, OutputProvider


class GameRuntime:
    """Runtime orchestrator for the chess game."""
    
    def __init__(
        self,
        initial_state: GameState,
        input_provider: Optional[InputProvider] = None,
        output_provider: Optional[OutputProvider] = None
    ):
        self.turn_service = TurnService(initial_state)
        self.repository = BoardRepository()
        self.repository.set_board(initial_state.board)
        self.input_provider = input_provider
        self.output_provider = output_provider
        self.promotion_pending: Optional[Move] = None
        self.pending_parser_state: Optional[GameState] = initial_state
    
    def run(self) -> None:
        """Run the main game loop."""
        while True:
            self._display_game()
            
            # Check for game over
            is_over, result = self.turn_service.is_game_over()
            if is_over:
                self._output(result)
                break
            
            # Get and execute move
            move = self._get_move()
            if move is None:
                self._output("Invalid move. Try again.")
                continue
            
            # Handle promotion if needed
            if self.turn_service.requires_promotion(move):
                self.promotion_pending = move
                self._output(f"Promotion! Choose: {'q', 'r', 'b', 'n'}")
                continue
            
            # Execute move
            try:
                self.turn_service.make_move(move)
                self.repository.save_state(self.turn_service.game_state)
            except Exception as e:
                self._output(f"Error: {e}")
                continue
        
        self._output("Game over!")
    
    def _display_game(self) -> None:
        """Display current game state."""
        history = self.turn_service.game_state.move_history.moves
        last_move = history[-1] if history else None
        
        # Delegate to output provider for rendering
        if self.output_provider:
            self.output_provider.display_board(self.turn_service.game_state)
            self.output_provider.display_game_info(self.turn_service.game_state, last_move)
            self.output_provider.display_message(self._format_move_history(history))
    
    def _get_move(self) -> Optional[Move]:
        """Get a valid move from the player."""
        if self.promotion_pending:
            # Handle promotion choice
            return self._handle_promotion()
        
        # Get input from player
        player_input = self._get_input()
        
        # Parse the move using runtime's own simple parser
        # (full algebraic parser is in ui layer which runtime cannot import)
        move = self._parse_move(player_input)
        
        # Validate move
        if move is None or not self.turn_service.is_move_valid(move):
            return None
        
        return move
    
    def _handle_promotion(self) -> Optional[Move]:
        """Handle pawn promotion choice."""
        move = self.promotion_pending
        player_input = self._get_input().strip().lower()
        
        choices = {
            'q': PieceType.QUEEN,
            'queen': PieceType.QUEEN,
            '1': PieceType.QUEEN,
            'r': PieceType.ROOK,
            'rook': PieceType.ROOK,
            '2': PieceType.ROOK,
            'b': PieceType.BISHOP,
            'bishop': PieceType.BISHOP,
            '3': PieceType.BISHOP,
            'n': PieceType.KNIGHT,
            'knight': PieceType.KNIGHT,
            '4': PieceType.KNIGHT
        }
        
        piece_type = choices.get(player_input)
        if piece_type is None:
            self._output("Invalid choice. Try again.")
            return None
        
        # Apply promotion
        move_with_promotion = Move(
            from_square=move.from_square,
            to_square=move.to_square,
            piece=move.piece,
            promotion_piece=piece_type,
            is_capture=move.is_capture
        )
        
        try:
            self.turn_service.make_move(move_with_promotion)
            self.repository.save_state(self.turn_service.game_state)
            self.promotion_pending = None
            self._output(f"Promoted to {piece_type.name.title()}!")
            return move_with_promotion
        except Exception as e:
            self._output(f"Error: {e}")
            return None
    
    def _parse_move(self, input_str: str) -> Optional[Move]:
        """Parse user input into a Move using runtime's own logic."""
        # Simplified parsing - uses two-square format like "e2e4"
        # Full algebraic notation parsing is in ui.parser.InputParser
        try:
            if len(input_str) >= 4:
                from_sq = input_str[0:2]
                to_sq = input_str[2:4]
                # This is a simplified parser - full implementation would validate
                return Move(
                    from_square=from_sq,
                    to_square=to_sq,
                    piece=None,  # Will be filled in by service
                    promotion_piece=None,
                    is_capture=False
                )
        except Exception:
            pass
        return None
    
    def _format_move_history(self, moves: list[Move]) -> str:
        """Format move history for display."""
        if not moves:
            return "No moves yet."
        
        move_strings = []
        for i, move in enumerate(moves):
            move_num = (i // 2) + 1
            color = "White" if i % 2 == 0 else "Black"
            move_str = f"{move_num}. {color}: {move.from_square} → {move.to_square}"
            move_strings.append(move_str)
        
        return "\n".join(move_strings)
    
    def _get_input(self) -> str:
        """Get input from player."""
        if self.input_provider:
            return self.input_provider.get_user_input()
        return input("Enter your move: ")
    
    def _output(self, message: str) -> None:
        """Output message to player."""
        if self.output_provider:
            self.output_provider.display_message(message)
        else:
            print(message)
