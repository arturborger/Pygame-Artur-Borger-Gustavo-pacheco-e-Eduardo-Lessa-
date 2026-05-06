"""Cena de estatísticas exibida ao fim da partida."""

from __future__ import annotations

import math

import pygame

from src.scenes.base_scene import BaseScene
from src.settings import BLACK, BLUE, GREEN_LOCKED, HEIGHT, ORANGE, WHITE, WIDTH, YELLOW


class StatsScene(BaseScene):
    """Mostra aces, winners e histórico de sets da partida.

    Args:
        game: Instância principal do jogo.
        score_manager: Placar oficial usado na partida encerrada.
        stats_tracker: Fachada com estatísticas simples da partida.
        mode: Modo de jogo que será repassado para a tela final.
        opponents_beaten: Quantidade opcional de adversários vencidos.

    Attributes:
        score_manager: Placar final da partida.
        stats_tracker: Estatísticas simples para consulta pela UI.
        mode: Modo de jogo da partida encerrada.
        opponents_beaten: Progresso opcional do torneio.
    """

    def __init__(
        self,
        game,
        score_manager,
        stats_tracker,
        mode: str = "1p",
        opponents_beaten: int | None = None,
    ) -> None:
        """Inicializa fontes e dados finais da partida."""
        super().__init__(game)
        self.score_manager = score_manager
        self.stats_tracker = stats_tracker
        self.mode = mode
        self.opponents_beaten = opponents_beaten
        self._next_scene = None
        self._title_font = pygame.font.Font(None, 58)
        self._title_font.set_bold(True)
        self._name_font = pygame.font.Font(None, 38)
        self._name_font.set_bold(True)
        self._body_font = pygame.font.Font(None, 30)
        self._small_font = pygame.font.Font(None, 24)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa avanço para a tela de fim de jogo.

        Args:
            events: Lista de eventos capturados no quadro atual.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._next_scene = self._build_game_over_scene()

    def update(self, dt: float) -> None:
        """Mantém a tela estática.

        Args:
            dt: Tempo decorrido desde o último quadro, sem uso nesta cena.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha título, colunas de jogadores e histórico de sets.

        Args:
            surface: Superfície principal onde a cena deve renderizar.
        """
        surface.fill(YELLOW)
        self._draw_background(surface)
        self._draw_title(surface)
        self._draw_player_card(surface, "p1", pygame.Rect(96, 138, 340, 330))
        self._draw_player_card(surface, "p2", pygame.Rect(524, 138, 340, 330))
        self._draw_history(surface)
        self._draw_hint(surface)

    def next_scene(self):
        """Retorna a próxima cena solicitada pela tela de estatísticas.

        Returns:
            GameOverScene quando disponível, ou ``None``.
        """
        next_scene = self._next_scene
        self._next_scene = None
        return next_scene

    def _build_game_over_scene(self):
        try:
            module = __import__(
                "src.scenes.game_over_scene",
                fromlist=["GameOverScene"],
            )
        except ModuleNotFoundError:
            return None

        scene_class = getattr(module, "GameOverScene")
        return scene_class(
            self.game,
            self._winner_name(),
            self.mode,
            self.opponents_beaten,
        )

    def _draw_background(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, ORANGE, (80, 78), 34)
        pygame.draw.circle(surface, BLACK, (80, 78), 34, width=4)
        pygame.draw.circle(surface, BLUE, (WIDTH - 82, 80), 30)
        pygame.draw.circle(surface, BLACK, (WIDTH - 82, 80), 30, width=4)

    def _draw_title(self, surface: pygame.Surface) -> None:
        self._draw_outlined_text(
            surface,
            "ESTATISTICAS DA PARTIDA",
            self._title_font,
            (WIDTH // 2, 70),
            WHITE,
        )

    def _draw_player_card(
        self,
        surface: pygame.Surface,
        side: str,
        rect: pygame.Rect,
    ) -> None:
        color = BLUE if side == "p1" else ORANGE
        pygame.draw.rect(surface, WHITE, rect, border_radius=14)
        pygame.draw.rect(surface, BLACK, rect, width=5, border_radius=14)
        pygame.draw.rect(
            surface,
            color,
            rect.inflate(-16, -16),
            width=4,
            border_radius=10,
        )

        name = self._player_name(side)
        sets = self._sets_won(side)
        stats = self.stats_tracker.get(side)
        rows = (
            ("Sets vencidos", str(sets), self._draw_set_icon),
            ("Aces", str(stats["aces"]), self._draw_ace_icon),
            ("Winners", str(stats["winners"]), self._draw_winner_icon),
        )

        name_text = self._name_font.render(name, True, BLACK)
        name_rect = name_text.get_rect(center=(rect.centerx, rect.top + 58))
        surface.blit(name_text, name_rect)

        y = rect.top + 126
        for label, value, icon_fn in rows:
            self._draw_stat_row(surface, rect, y, label, value, icon_fn)
            y += 74

    def _draw_stat_row(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        y: int,
        label: str,
        value: str,
        icon_fn,
    ) -> None:
        icon_center = (rect.left + 62, y)
        icon_fn(surface, icon_center)
        label_text = self._body_font.render(label, True, BLACK)
        value_text = self._body_font.render(value, True, BLACK)
        surface.blit(label_text, (rect.left + 98, y - 16))
        surface.blit(value_text, value_text.get_rect(midright=(rect.right - 40, y)))

    def _draw_history(self, surface: pygame.Surface) -> None:
        history_rect = pygame.Rect(132, 492, WIDTH - 264, 54)
        pygame.draw.rect(surface, WHITE, history_rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, history_rect, width=4, border_radius=12)
        history = self._sets_history_text()
        text = self._body_font.render(f"Sets: {history}", True, BLACK)
        surface.blit(text, text.get_rect(center=history_rect.center))

    def _draw_hint(self, surface: pygame.Surface) -> None:
        hint = self._small_font.render("ENTER para continuar", True, BLACK)
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 28)))

    def _draw_set_icon(
        self,
        surface: pygame.Surface,
        center: tuple[int, int],
    ) -> None:
        pygame.draw.circle(surface, BLACK, center, 18)
        pygame.draw.circle(surface, GREEN_LOCKED, center, 13)

    def _draw_ace_icon(
        self,
        surface: pygame.Surface,
        center: tuple[int, int],
    ) -> None:
        pygame.draw.circle(surface, BLACK, center, 18)
        pygame.draw.circle(surface, YELLOW, center, 13)
        arc_rect = pygame.Rect(center[0] - 12, center[1] - 10, 20, 20)
        pygame.draw.arc(surface, WHITE, arc_rect, -1.2, 1.2, 2)

    def _draw_winner_icon(
        self,
        surface: pygame.Surface,
        center: tuple[int, int],
    ) -> None:
        points = []
        for index in range(10):
            radius = 18 if index % 2 == 0 else 8
            angle = math.radians(-90 + index * 36)
            points.append(
                (
                    center[0] + round(math.cos(angle) * radius),
                    center[1] + round(math.sin(angle) * radius),
                )
            )

        pygame.draw.polygon(surface, BLACK, points)
        inner_points = [
            (
                center[0] + round((point[0] - center[0]) * 0.7),
                center[1] + round((point[1] - center[1]) * 0.7),
            )
            for point in points
        ]
        pygame.draw.polygon(surface, ORANGE, inner_points)

    def _draw_outlined_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        text_rect = font.render(text, True, color).get_rect(center=center)
        for offset_x, offset_y in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            outline = font.render(text, True, BLACK)
            surface.blit(outline, text_rect.move(offset_x, offset_y))

        rendered = font.render(text, True, color)
        surface.blit(rendered, text_rect)

    def _player_name(self, side: str) -> str:
        if side == "p1":
            return self.score_manager.p1_name

        return self.score_manager.p2_name

    def _sets_won(self, side: str) -> int:
        p1_sets, p2_sets = self.score_manager.sets_won()
        return p1_sets if side == "p1" else p2_sets

    def _sets_history_text(self) -> str:
        history = getattr(self.score_manager, "_sets_history", [])
        if not history:
            return "sem sets fechados"

        return " · ".join(f"{p1_games}-{p2_games}" for p1_games, p2_games in history)

    def _winner_name(self) -> str:
        winner = self.score_manager.winner()
        if winner == "p1":
            return self.score_manager.p1_name
        if winner == "p2":
            return self.score_manager.p2_name
        return "Sem vencedor"
