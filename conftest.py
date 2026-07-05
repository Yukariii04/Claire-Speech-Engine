"""Root conftest — ensure the cse *package* is found, not the cse.py script."""

import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent)
_src = str(Path(_root) / "src")

# Aggressively remove any path that resolves to the project root
_root_resolved = Path(_root).resolve()
sys.path = [_src] + [
    p for p in sys.path
    if p not in (_root, "", ".")
    and (not p or Path(p).resolve() != _root_resolved)
]

# Also forcibly place the correct package in sys.modules
# so pytest's assertion rewriter finds it, not cse.py
import importlib.util

_pkg_init = str(Path(_src) / "cse" / "__init__.py")
_spec = importlib.util.spec_from_file_location(
    "cse",
    _pkg_init,
    submodule_search_locations=[str(Path(_src) / "cse")],
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["cse"] = _mod
_spec.loader.exec_module(_mod)
