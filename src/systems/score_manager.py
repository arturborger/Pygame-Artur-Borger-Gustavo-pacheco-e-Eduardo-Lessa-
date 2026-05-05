"""Gerenciamento da pontuacao oficial do tenis."""

from __future__ import annotations

from src.settings import GAME_TARGET_POINTS


class ScoreManager:
    """Gerencia pontuacao oficial do tenis.

    Args:
        p1_name: Nome exibido para o jogador 1.
        p2_name: Nome exibido para o jogador 2.

    Attributes:
        p1_name: Nome do jogador 1.
        p2_name: Nome do jogador 2.
    """

    _POINT_LABELS = ("0", "15", "30", "40")
    _VALID_SIDES = ("p1", "p2")
    _VALID_POINT_TYPES = ("normal", "ace", "winner")

    def __init__(self, p1_name: str, p2_name: str) -> None:
        """Inicializa uma partida com placar zerado.

        Args:
            p1_name: Nome exibido para o jogador 1.
            p2_name: Nome exibido para o jogador 2.
        """
        self.p1_name = p1_name
        self.p2_name = p2_name
        self._game_points = {"p1": 0, "p2": 0}
        self._set_games = {"p1": 0, "p2": 0}
        self._sets_won = {"p1": 0, "p2": 0}
        self._sets_history: list[tuple[int, int]] = []
        self._server = "p1"
        self._stats = {
            "p1": {"aces": 0, "winners": 0},
            "p2": {"aces": 0, "winners": 0},
        }

    def add_point(self, winner_side: str, point_type: str = "normal") -> None:
        """Registra um ponto e atualiza o placar do game.

        Args:
            winner_side: Lado vencedor do ponto, ``"p1"`` ou ``"p2"``.
            point_type: Tipo do ponto, ``"ace"``, ``"winner"`` ou ``"normal"``.

        Raises:
            ValueError: Se o lado ou o tipo do ponto forem invalidos.
        """
        self._validate_side(winner_side)
        self._validate_point_type(point_type)

        self._game_points[winner_side] += 1
        if point_type == "ace":
            self._stats[winner_side]["aces"] += 1
        elif point_type == "winner":
            self._stats[winner_side]["winners"] += 1

        self._check_game_winner()

    def current_game_score(self) -> tuple[str, str]:
        """Retorna o placar textual do game atual.

        Returns:
            Tupla com o placar de ``p1`` e ``p2`` usando ``0``, ``15``, ``30``,
            ``40`` e ``AD``.
        """
        p1_points = self._game_points["p1"]
        p2_points = self._game_points["p2"]

        if p1_points >= 3 and p2_points >= 3:
            diff = p1_points - p2_points
            if diff == 0:
                return "40", "40"
            if diff > 0:
                return "AD", "40"
            return "40", "AD"

        p1_score = self._POINT_LABELS[min(p1_points, 3)]
        p2_score = self._POINT_LABELS[min(p2_points, 3)]
        return p1_score, p2_score

    def stats(self, side: str) -> dict[str, int]:
        """Retorna uma copia das estatisticas simples do lado informado.

        Args:
            side: Lado consultado, ``"p1"`` ou ``"p2"``.

        Returns:
            Dicionario com as chaves ``"aces"`` e ``"winners"``.

        Raises:
            ValueError: Se o lado informado for invalido.
        """
        self._validate_side(side)
        return self._stats[side].copy()

    def _check_game_winner(self) -> None:
        p1_points = self._game_points["p1"]
        p2_points = self._game_points["p2"]
        diff = p1_points - p2_points

        if p1_points >= 3 and p2_points >= 3:
            if diff >= 2:
                self._finish_game("p1")
            elif diff <= -2:
                self._finish_game("p2")
            return

        if p1_points >= GAME_TARGET_POINTS and diff >= 2:
            self._finish_game("p1")
        elif p2_points >= GAME_TARGET_POINTS and diff <= -2:
            self._finish_game("p2")

    def _finish_game(self, winner_side: str) -> None:
        self._game_points = {"p1": 0, "p2": 0}
        self._on_game_won(winner_side)

    def _on_game_won(self, side: str) -> None:
        self._set_games[side] += 1

    def _validate_side(self, side: str) -> None:
        if side not in self._VALID_SIDES:
            raise ValueError(f"Lado invalido: {side!r}. Use 'p1' ou 'p2'.")

    def _validate_point_type(self, point_type: str) -> None:
        if point_type not in self._VALID_POINT_TYPES:
            raise ValueError(
                "Tipo de ponto invalido: "
                f"{point_type!r}. Use 'normal', 'ace' ou 'winner'."
            )


if __name__ == "__main__":
    manager = ScoreManager("Voce", "CPU")
    for _ in range(4):
        manager.add_point("p1")
    assert manager.current_game_score() == ("0", "0")
    assert manager._set_games == {"p1": 1, "p2": 0}

    manager = ScoreManager("Voce", "CPU")
    for _ in range(3):
        manager.add_point("p1")
        manager.add_point("p2")
    assert manager.current_game_score() == ("40", "40")
    manager.add_point("p1")
    assert manager.current_game_score() == ("AD", "40")
    manager.add_point("p2")
    assert manager.current_game_score() == ("40", "40")
    manager.add_point("p1")
    assert manager.current_game_score() == ("AD", "40")
    manager.add_point("p1")
    assert manager.current_game_score() == ("0", "0")
    assert manager._set_games == {"p1": 1, "p2": 0}

    manager = ScoreManager("Voce", "CPU")
    for _ in range(3):
        manager.add_point("p1")
    assert manager.current_game_score() == ("40", "0")
    assert manager._set_games == {"p1": 0, "p2": 0}
