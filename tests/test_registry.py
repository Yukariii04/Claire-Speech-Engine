"""Tests for the module registry."""

from __future__ import annotations

import pytest

from cse.core.registry import ModuleRegistry


class TestModuleRegistry:
    """ModuleRegistry unit tests."""

    def test_register_and_get(self) -> None:
        reg = ModuleRegistry()
        reg.register("test_mod", {"hello": "world"})
        assert reg.get("test_mod") == {"hello": "world"}

    def test_duplicate_register_raises(self) -> None:
        reg = ModuleRegistry()
        reg.register("dup", object())
        with pytest.raises(ValueError, match="already registered"):
            reg.register("dup", object())

    def test_get_missing_raises(self) -> None:
        reg = ModuleRegistry()
        with pytest.raises(KeyError, match="not registered"):
            reg.get("ghost")

    def test_is_registered(self) -> None:
        reg = ModuleRegistry()
        assert not reg.is_registered("thing")
        reg.register("thing", 42)
        assert reg.is_registered("thing")

    def test_list_modules(self) -> None:
        reg = ModuleRegistry()
        reg.register("b_mod", 2)
        reg.register("a_mod", 1)
        assert reg.list_modules() == ["a_mod", "b_mod"]

    def test_len(self) -> None:
        reg = ModuleRegistry()
        assert len(reg) == 0
        reg.register("x", None)
        assert len(reg) == 1

    def test_repr(self) -> None:
        reg = ModuleRegistry()
        reg.register("alpha", 1)
        assert "alpha" in repr(reg)
