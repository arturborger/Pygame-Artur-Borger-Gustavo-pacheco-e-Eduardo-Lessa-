"""Gerenciamento da pontuacao oficial do tenis."""

from __future__ import annotations

from src.settings import (
    GAME_TARGET_POINTS,
    GAMES_TARGET_SET,
    SETS_TO_WIN_MATCH,
    TIEBREAK_TARGET,
)


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
        self._is_tiebreak = False
        self._tiebreak_start_server: str | None = None
        self._match_over = False
        self._match_winner: str | None = None
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
        if self._match_over:
            return

        self._validate_side(winner_side)
        self._validate_point_type(point_type)

        self._game_points[winner_side] += 1
        if point_type == "ace":
            self._stats[winner_side]["aces"] += 1
        elif point_type == "winner":
            self._stats[winner_side]["winners"] += 1

        self._check_game_winner()
        if self._is_tiebreak:
            self._update_tiebreak_server_after_point()

    def current_game_score(self) -> tuple[str, str]:
        """Retorna o placar textual do game atual.

        Returns:
            Tupla com o placar de ``p1`` e ``p2`` usando ``0``, ``15``, ``30``,
            ``40`` e ``AD``.
        """
        p1_points = self._game_points["p1"]
        p2_points = self._game_points["p2"]

        if self._is_tiebreak:
            return str(p1_points), str(p2_points)

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

    def is_tiebreak(self) -> bool:
        """Indica se o game atual e um tie-break.

        Returns:
            ``True`` quando o set esta empatado em 6-6 e os pontos seguem a
            regra numerica do tie-break.
        """
        return self._is_tiebreak

    def current_set_games(self) -> tuple[int, int]:
        """Retorna os games vencidos no set atual.

        Returns:
            Tupla ``(games_p1, games_p2)``.
        """
        return self._set_games["p1"], self._set_games["p2"]

    def sets_won(self) -> tuple[int, int]:
        """Retorna a quantidade de sets vencidos por cada lado.

        Returns:
            Tupla ``(sets_p1, sets_p2)``.
        """
        return self._sets_won["p1"], self._sets_won["p2"]

    def server(self) -> str:
        """Retorna o lado que deve sacar o proximo ponto.

        Returns:
            ``"p1"`` ou ``"p2"``.
        """
        return self._server

    def is_match_over(self) -> bool:
        """Indica se a partida ja terminou.

        Returns:
            ``True`` quando algum lado venceu a melhor de tres sets.
        """
        return self._match_over

    def winner(self) -> str | None:
        """Retorna o vencedor da partida, se houver.

        Returns:
            ``"p1"``, ``"p2"`` ou ``None`` se a partida ainda estiver ativa.
        """
        return self._match_winner

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

        if self._is_tiebreak:
            if p1_points >= TIEBREAK_TARGET and diff >= 2:
                self._finish_tiebreak("p1")
            elif p2_points >= TIEBREAK_TARGET and diff <= -2:
                self._finish_tiebreak("p2")
            return

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
        self._toggle_server()
        self._check_set_winner()

    def _check_set_winner(self) -> None:
        p1_games = self._set_games["p1"]
        p2_games = self._set_games["p2"]
        max_games = max(p1_games, p2_games)
        diff = p1_games - p2_games

        if max_games >= GAMES_TARGET_SET and abs(diff) >= 2:
            winner_side = "p1" if diff > 0 else "p2"
            self._on_set_won(winner_side)
            return

        if p1_games == GAMES_TARGET_SET and p2_games == GAMES_TARGET_SET:
            self._is_tiebreak = True
            self._tiebreak_start_server = self._server
            self._game_points = {"p1": 0, "p2": 0}

    def _finish_tiebreak(self, winner_side: str) -> None:
        first_server = self._tiebreak_start_server or self._server
        self._server = self._other_side(first_server)
        self._game_points = {"p1": 0, "p2": 0}
        self._set_games[winner_side] += 1
        self._on_set_won(winner_side)

    def _on_set_won(self, side: str) -> None:
        self._sets_won[side] += 1
        self._sets_history.append((self._set_games["p1"], self._set_games["p2"]))
        self._set_games = {"p1": 0, "p2": 0}
        self._game_points = {"p1": 0, "p2": 0}
        self._is_tiebreak = False
        self._tiebreak_start_server = None
        if self._sets_won[side] >= SETS_TO_WIN_MATCH:
            self._match_over = True
            self._match_winner = side

    def _update_tiebreak_server_after_point(self) -> None:
        total_points = self._game_points["p1"] + self._game_points["p2"]
        if total_points % 2 == 1:
            self._toggle_server()

    def _toggle_server(self) -> None:
        self._server = self._other_side(self._server)

    def _other_side(self, side: str) -> str:
        return "p2" if side == "p1" else "p1"

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
    def win_regular_game(score_manager: ScoreManager, side: str) -> None:
        for _ in range(4):
            score_manager.add_point(side)


    manager = ScoreManager("Voce", "CPU")
    win_regular_game(manager, "p1")
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

    manager = ScoreManager("Voce", "CPU")
    assert manager.server() == "p1"
    win_regular_game(manager, "p1")
    assert manager.server() == "p2"
    win_regular_game(manager, "p2")
    assert manager.server() == "p1"

    manager = ScoreManager("Voce", "CPU")
    for _ in range(6):
        win_regular_game(manager, "p1")
    assert manager.sets_won() == (1, 0)
    assert manager._sets_history == [(6, 0)]
    assert manager.current_set_games() == (0, 0)

    manager = ScoreManager("Voce", "CPU")
    for _ in range(6):
        win_regular_game(manager, "p1")
        win_regular_game(manager, "p2")
    assert manager.is_tiebreak()
    assert manager._set_games == {"p1": 6, "p2": 6}
    assert manager.current_game_score() == ("0", "0")

    for _ in range(5):
        manager.add_point("p1")
        manager.add_point("p2")
    manager.add_point("p1")
    manager.add_point("p1")
    assert not manager.is_tiebreak()
    assert manager.sets_won() == (1, 0)
    assert manager._sets_history == [(7, 6)]

    manager = ScoreManager("Voce", "CPU")
    for _ in range(6):
        win_regular_game(manager, "p1")
        win_regular_game(manager, "p2")
    assert manager.is_tiebreak()
    assert manager.server() == "p1"
    manager.add_point("p1")
    assert manager.server() == "p2"
    manager.add_point("p1")
    assert manager.server() == "p2"
    manager.add_point("p1")
    assert manager.server() == "p1"

    manager = ScoreManager("Voce", "CPU")
    for _ in range(6):
        win_regular_game(manager, "p1")
    for _ in range(6):
        win_regular_game(manager, "p1")
    assert manager.is_match_over()
    assert manager.winner() == "p1"
    assert manager.sets_won() == (2, 0)

    manager = ScoreManager("Voce", "CPU")
    for _ in range(6):
        win_regular_game(manager, "p1")
    for _ in range(6):
        win_regular_game(manager, "p2")
    for _ in range(6):
        win_regular_game(manager, "p1")
        win_regular_game(manager, "p2")
    for _ in range(5):
        manager.add_point("p1")
        manager.add_point("p2")
    manager.add_point("p1")
    manager.add_point("p1")
    assert manager.is_match_over()
    assert manager.winner() == "p1"
    assert manager.sets_won() == (2, 1)

    manager = ScoreManager("Voce", "CPU")
    manager.add_point("p1", "ace")
    manager.add_point("p2", "winner")
    assert manager.stats("p1") == {"aces": 1, "winners": 0}
    assert manager.stats("p2") == {"aces": 0, "winners": 1}
