# Source Architecture

Every source file lives in exactly one layer directory under `src/`. Layer
dependencies are enforced mechanically by `lint.py` at the repo root.

## Layers

| Layer       | Purpose                                                  | May import from                                              |
|-------------|----------------------------------------------------------|--------------------------------------------------------------|
| `types`     | Pure type definitions; no logic.                         | `types`                                                      |
| `config`    | Constants, settings, environment.                        | `types`, `config`                                            |
| `repo`      | Data access — DB, files, external state.                 | `types`, `config`, `repo`                                    |
| `service`   | Business logic.                                          | `types`, `config`, `repo`, `providers`, `service`            |
| `runtime`   | App lifecycle, orchestration, wiring.                    | `types`, `config`, `repo`, `service`, `providers`, `runtime` |
| `ui`        | User-facing surfaces — CLI, web, GUI.                    | `types`, `config`, `service`, `runtime`, `providers`, `ui`   |
| `providers` | Cross-cutting: auth, telemetry, connectors, flags.       | `types`, `config`, `utils`, `providers`                      |
| `utils`     | Pure helpers; no domain logic, no internal imports.      | `utils`                                                      |

The forward chain is `types → config → repo → service → runtime → ui`.
`providers` is the only legal entry point for cross-cutting concerns.
`utils` is leaf; nothing internal may live there beyond pure functions.

## Rules

1. Every file under `src/` belongs in exactly one layer directory.
2. Imports may only target layers in the file's own "may import from" set.
3. No file exceeds 300 lines — split into smaller modules within the same layer.
4. **Parse-don't-validate at boundaries**: at every system entry point (user
   input, network, file I/O), parse incoming data into a type from `types/`.
   Internal code trusts the type and never re-validates.
5. Tests live under `tests/` (not under `src/`) and are not lint-checked here.

Run `python lint.py` to verify. The runner runs it as a final gate.
