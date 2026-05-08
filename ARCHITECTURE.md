# Architecture Document

This document describes the architecture of the terminal chess game.

## Overview

A chess game for two players, playable from Linux terminal using formal chess notation (e.g., "Ke8"). Supports standard chess features including castling, en passant, pawn promotion, check, and checkmate.

## Layers

### types
Pure type definitions only. No logic.
- `__init__.py` - exports all types
- `pieces.py` - Piece, Color, Square types
- `game.py` - GameState, Move, MoveHistory types

### config
Constants and settings.
- `__init__.py` - exports configuration
- `constants.py` - board dimensions, starting positions

### repo
Data access and persistence.
- `__init__.py` - exports repo interface
- `board.py` - BoardRepository (store/retrieve board state)

### service
Business logic.
- `__init__.py` - exports service interface
- `validation.py` - move validation logic
- `rules.py` - castling, en passant, promotion rules
- `check.py` - check/checkmate detection
- `turn.py` - turn management

### providers
Cross-cutting concerns.
- `__init__.py` - exports providers
- `input.py` - InputProvider (parse user input)
- `output.py` - OutputProvider (display to terminal)

### runtime
Orchestration and lifecycle.
- `__init__.py` - exports runtime functions
- `game_loop.py` - main game loop
- `wiring.py` - dependency injection

### ui
User interface.
- `__init__.py` - exports UI functions
- `display.py` - render board to terminal
- `input_parser.py` - parse chess notation

### utils
Pure helpers.
- `__init__.py` - exports utilities
- `string.py` - string manipulation helpers
- `validation.py` - pure validation helpers

## Layer Dependencies

```
types ← config ← repo ← service ← runtime ← ui
                    ↑                    ↑
                    └── providers ──────┘
                    ↑
              utils ←┘ (utils is leaf, nothing imports it)
```

- `types`: can only import from itself
- `config`: can import from types, config
- `repo`: can import from types, config, repo
- `service`: can import from types, config, repo, providers, service
- `providers`: can import from types, config, utils, providers
- `runtime`: can import from types, config, repo, service, providers, runtime
- `ui`: can import from types, config, service, runtime, providers, ui
- `utils`: can only import from itself

## Entry Points

- `main.py` at repo root - entry point for running the game
- `python -m terminal_chess_cli_2339.src.runtime` - alternative entry

## Parsing Strategy

At every boundary (user input, file I/O), parse into types before passing to business logic.
Internal code trusts the parsed types and never re-validates.

User input → Parse → Move type → Service → Update Board
