"""Fachada simples para estatisticas exibidas pela interface."""

from __future__ import annotations


class StatsTracker:
    """Armazena aces e winners sem expor o ScoreManager inteiro."""

    _VALID_SIDES = ("p1", "p2")

    def __init__(self) -> None:
        """Inicializa as estatisticas zeradas para os dois lados."""
        self._stats = self._empty_stats()

    def register_ace(self, side: str) -> None:
        """Registra um ace para o lado informado.

        Args:
            side: Lado pontuador, ``"p1"`` ou ``"p2"``.

        Raises:
            ValueError: Se o lado informado for invalido.
        """
        self._validate_side(side)
        self._stats[side]["aces"] += 1

    def register_winner(self, side: str) -> None:
        """Registra um winner para o lado informado.

        Args:
            side: Lado pontuador, ``"p1"`` ou ``"p2"``.

        Raises:
            ValueError: Se o lado informado for invalido.
        """
        self._validate_side(side)
        self._stats[side]["winners"] += 1

    def get(self, side: str) -> dict[str, int]:
        """Retorna uma copia das estatisticas do lado solicitado.

        Args:
            side: Lado consultado, ``"p1"`` ou ``"p2"``.

        Returns:
            Dicionario com as chaves ``"aces"`` e ``"winners"``.

        Raises:
            ValueError: Se o lado informado for invalido.
        """
        self._validate_side(side)
        return self._stats[side].copy()

    def reset(self) -> None:
        """Zera aces e winners dos dois jogadores."""
        self._stats = self._empty_stats()

    def _empty_stats(self) -> dict[str, dict[str, int]]:
        return {
            "p1": {"aces": 0, "winners": 0},
            "p2": {"aces": 0, "winners": 0},
        }

    def _validate_side(self, side: str) -> None:
        if side not in self._VALID_SIDES:
            raise ValueError(f"Lado invalido: {side!r}. Use 'p1' ou 'p2'.")
