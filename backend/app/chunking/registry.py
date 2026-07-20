"""Registry for selecting chunking strategies at runtime."""

from __future__ import annotations

from collections.abc import Iterable

from app.chunking.domain import ChunkingStrategyType
from app.chunking.ports import ChunkingStrategy


class StrategyNotRegisteredError(LookupError):
    """Raised when no strategy is registered for a requested type."""


class ChunkingStrategyRegistry:
    """Mutable composition-root registry for Strategy pattern implementations."""

    def __init__(self, strategies: Iterable[ChunkingStrategy] = ()) -> None:
        self._strategies: dict[ChunkingStrategyType, ChunkingStrategy] = {}
        for strategy in strategies:
            self.register(strategy)

    def register(self, strategy: ChunkingStrategy) -> None:
        """Register or replace a strategy implementation."""

        self._strategies[strategy.strategy_type] = strategy

    def get(self, strategy_type: ChunkingStrategyType) -> ChunkingStrategy:
        """Resolve a strategy by type."""

        try:
            return self._strategies[strategy_type]
        except KeyError as exc:
            raise StrategyNotRegisteredError(
                f"No chunking strategy registered for '{strategy_type.value}'"
            ) from exc
