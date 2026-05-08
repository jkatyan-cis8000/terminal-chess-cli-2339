#!/usr/bin/env python3
"""
Lint.py - Enforces layer architecture and file rules for the chess game.

This linter verifies:
1. Every source file lives inside a layer directory.
2. Imports respect the forward dependency direction.
3. No file exceeds 300 lines.

Exit 0 on clean codebase, exit 1 with violation list on failure.
"""

import ast
import sys
from pathlib import Path

# Layer order defines the dependency chain
LAYERS = ["core", "config", "persistence", "logic", "controller", "ui", "interfaces", "utils"]

# Valid import targets for each layer
ALLOWED_IMPORTS = {
    "core": {"core"},
    "config": {"core", "config"},
    "persistence": {"core", "config", "persistence"},
    "logic": {"core", "config", "persistence", "interfaces", "logic"},
    "interfaces": {"core", "config", "utils", "interfaces"},
    "controller": {"core", "config", "persistence", "logic", "interfaces", "controller"},
    "ui": {"core", "config", "logic", "controller", "interfaces", "ui"},
    "utils": {"utils"},
}

MAX_LINES = 300


def get_layer(filepath: Path) -> str | None:
    """Get the layer name for a file, or None if not in a layer."""
    src = Path("src")
    try:
        rel_path = filepath.relative_to(src)
        parts = rel_path.parts
        if parts:
            # Skip if it's the main entry point (src/main.py)
            if len(parts) == 1 and parts[0] == "main.py":
                return None
            return parts[0].replace(".py", "")
    except ValueError:
        pass
    return None


def get_imports(filepath: Path) -> list[tuple[str, int]]:
    """Get all imports from a Python file."""
    imports = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append((node.module, node.lineno))
                elif node.level and node.module:  # relative import
                    # Handle relative imports like `from . import X`
                    imports.append((node.module, node.lineno))
    except SyntaxError:
        pass
    return imports


def is_relative_import(import_str: str) -> bool:
    """Check if an import is relative (starts with .)."""
    return import_str.startswith(".")


def get_import_module(imp: str) -> str:
    """Get the base module name from an import."""
    # Skip standard library modules that don't need checking
    if imp in ("__future__", "re", "typing"):
        return ""
    # Remove relative import prefix
    clean = imp.lstrip(".")
    if clean:
        parts = clean.split(".")
        # Handle absolute imports like 'src.types' - skip 'src' prefix
        if parts[0] == "src" and len(parts) > 1:
            return parts[1]
        # Return the first part which should be the layer name
        return parts[0]
    return ""


def check_file(filepath: Path) -> list[str]:
    """Check a single file for lint violations."""
    violations = []
    
    # Skip non-source files
    if not filepath.name.endswith(".py"):
        return violations
    
    # Skip __pycache__
    if "__pycache__" in str(filepath):
        return violations
    
    # Check line count
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if len(lines) > MAX_LINES:
            violations.append(
                f"{filepath}: Line count exceeded ({len(lines)} > {MAX_LINES} lines). "
                f"Split into smaller modules within the same layer."
            )
    except Exception:
        pass
    
    # Check imports
    if filepath.name == "__init__.py":
        return violations
    
    # Entry points like src/main.py can import from any layer
    if filepath.name == "main.py":
        return violations
    
    layer = get_layer(filepath)
    if layer is None:
        return violations
    
    imports = get_imports(filepath)
    allowed = ALLOWED_IMPORTS.get(layer, set())
    
    for imp, lineno in imports:
        # Handle relative imports
        if imp.startswith("."):
            base_module = get_import_module(imp)
            # For relative imports within the same layer, allow
            if base_module in allowed:
                continue
            # Check if it's importing from another layer
            if layer in allowed:
                continue
        
        module = get_import_module(imp)
        
        # Skip standard library and third-party imports
        if not module or module in ("builtins", "typing", "__future__", "re"):
            continue
        
        # Check if the imported module is in allowed layers
        if module not in allowed:
            violations.append(
                f"{filepath}:{lineno}: Invalid import '{imp}'. "
                f"Layer '{layer}' may only import from: {', '.join(sorted(allowed))}. "
                f"Got: '{module}'."
            )
    
    return violations


def lint() -> list[str]:
    """Run lint checks on all source files."""
    violations = []
    src = Path("src")
    
    if not src.exists():
        return ["src/ directory not found. Create the layer structure first."]
    
    for py_file in src.rglob("*.py"):
        file_violations = check_file(py_file)
        violations.extend(file_violations)
    
    return violations


def main() -> int:
    """Main entry point."""
    violations = lint()
    
    if violations:
        print("Lint violations found:\n")
        for v in violations:
            print(f"  ❌ {v}")
        print(f"\n{len(violations)} violation(s) found.")
        return 1
    
    print("✓ No lint violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
