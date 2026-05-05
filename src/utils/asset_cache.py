"""Cache simples para assets gerados em runtime."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import TypeVar, cast

T = TypeVar("T")


class AssetCache:
    """Armazena assets criados sob demanda e reutiliza chamadas futuras.

    Attributes:
        _items: Dicionario interno que associa chaves aos assets ja criados.
    """

    def __init__(self) -> None:
        """Inicializa o cache vazio."""
        self._items: dict[Hashable, object] = {}

    def get(self, key: Hashable, factory_fn: Callable[[], T]) -> T:
        """Retorna um asset do cache ou cria um novo usando a fabrica.

        Args:
            key: Chave usada para identificar o asset no cache.
            factory_fn: Funcao sem argumentos que cria o asset caso ele ainda
                nao exista no cache.

        Returns:
            Asset associado a `key`, reutilizando o objeto ja armazenado quando
            possivel.
        """
        if key not in self._items:
            self._items[key] = factory_fn()

        return cast(T, self._items[key])
