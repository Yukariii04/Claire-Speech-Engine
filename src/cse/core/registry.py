"""Module registry — register / discover pattern for runtime modules."""

from __future__ import annotations

from typing import Any


# ponytail: single global instance, factory if multi-registry ever needed
_instance: ModuleRegistry | None = None


class ModuleRegistry:
    """Central registry where every CSE module registers itself.

    Usage::

        registry = ModuleRegistry()
        registry.register("tokenizer", tokenizer_instance)
        registry.get("tokenizer")
    """

    def __init__(self) -> None:
        self._modules: dict[str, Any] = {}

    def register(self, name: str, module: Any) -> None:
        """Register a module under *name*.

        Args:
            name: Unique identifier for the module.
            module: The module or object to register.

        Raises:
            ValueError: If *name* is already registered.
        """
        if name in self._modules:
            raise ValueError(f"Module '{name}' is already registered.")
        self._modules[name] = module

    def get(self, name: str) -> Any:
        """Retrieve a registered module by name.

        Args:
            name: The identifier used during registration.

        Raises:
            KeyError: If *name* was never registered.
        """
        if name not in self._modules:
            raise KeyError(f"Module '{name}' is not registered.")
        return self._modules[name]

    def is_registered(self, name: str) -> bool:
        """Check whether *name* exists in the registry."""
        return name in self._modules

    def list_modules(self) -> list[str]:
        """Return sorted list of registered module names."""
        return sorted(self._modules)

    def __len__(self) -> int:
        return len(self._modules)

    def __repr__(self) -> str:
        names = ", ".join(self.list_modules())
        return f"ModuleRegistry([{names}])"


def get_registry() -> ModuleRegistry:
    """Return the global ``ModuleRegistry`` singleton.

    Raises:
        RuntimeError: If called before runtime initialisation.
    """
    if _instance is None:
        raise RuntimeError("Registry not initialised — call bootstrap() first.")
    return _instance


def _set_registry(instance: ModuleRegistry) -> None:
    """Set the global registry instance (called by bootstrap)."""
    global _instance
    _instance = instance
