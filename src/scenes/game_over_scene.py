"""Cena de fim de jogo com resultado e highscore."""

from __future__ import annotations

import math

import pygame

from src.assets_generator import make_button, make_trophy
from src.scenes.base_scene import BaseScene
from src.scenes.menu_scene import MenuScene
from src.settings import BLACK, BLUE, HEIGHT, ORANGE, TOURNAMENT_OPPONENTS, WHITE, WIDTH


class GameOverScene(BaseScene):
    """Exibe vitória ou derrota e salva o resultado da partida.

    Args:
        game: Instância principal do jogo.
        winner_name: Nome do vencedor da partida.
        mode: Modo de jogo encerrado.
        opponents_beaten: Quantidade opcional de adversários vencidos.

    Attributes:
        winner_name: Nome do vencedor da partida.
        mode: Modo de jogo encerrado.
        opponents_beaten: Progresso usado no highscore.
    """

    def __init__(
        self,
        game,
        winner_name: str,
        mode: str,
        opponents_beaten: int | None = None,
    ) -> None:
        """Inicializa a tela final, progresso e salvamento de recorde."""
        super().__init__(game)
        self.winner_name = winner_name
        self.mode = mode
        self.player_won = mode == "2p" or winner_name in ("Voce", "Você")
        self.opponents_beaten = self._resolve_opponents_beaten(opponents_beaten)
        self._next_scene = None
        self._title_font = pygame.font.Font(None, 82)
        self._title_font.set_bold(True)
        self._body_font = pygame.font.Font(None, 34)
        self._small_font = pygame.font.Font(None, 24)
        self._save_result()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa retorno ao menu ou ao mapa do torneio.

        Args:
            events: Lista de eventos capturados no quadro atual.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._next_scene = self._build_return_scene()

    def update(self, dt: float) -> None:
        """Mantém a tela estática, exceto pela animação desenhada do troféu.

        Args:
            dt: Tempo decorrido desde o último quadro, sem uso nesta cena.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha resultado, troféu quando aplicável e botão de retorno.

        Args:
            surface: Superfície principal onde a cena deve renderizar.
        """
        surface.fill(ORANGE if self.player_won else BLUE)
        self._draw_background(surface)
        if self.mode == "2p":
            title = "FIM DE JOGO"
        else:
            title = "VITÓRIA!" if self.player_won else "DERROTA"
        self._draw_outlined_text(surface, title, self._title_font, (WIDTH // 2, 98))
        self._draw_result_details(surface)
        if self.mode == "1p" and self.player_won:
            self._draw_animated_trophy(surface)
        self._draw_return_button(surface)

    def next_scene(self):
        """Retorna a próxima cena escolhida pelo jogador.

        Returns:
            TournamentScene, MenuScene ou ``None``.
        """
        next_scene = self._next_scene
        self._next_scene = None
        return next_scene

    def _resolve_opponents_beaten(self, opponents_beaten: int | None) -> int:
        current_progress = getattr(self.game, "tournament_progress", 0)
        if self.mode != "1p":
            return opponents_beaten or 0

        if self.player_won:
            new_progress = min(current_progress + 1, len(TOURNAMENT_OPPONENTS))
            self.game.tournament_progress = new_progress
            return new_progress

        return current_progress if opponents_beaten is None else opponents_beaten

    def _save_result(self) -> None:
        highscore_manager = getattr(self.game, "highscore_manager", None)
        if highscore_manager is None:
            return

        if self.mode == "1p":
            highscore_manager.add_tournament_record("Voce", self.opponents_beaten)
        elif self.mode == "2p":
            highscore_manager.add_2p_record(self.winner_name, 1)
        elif self.mode == "training":
            highscore_manager.add_training_record(self.winner_name, 0)

    def _build_return_scene(self):
        if self.mode == "1p" and self.opponents_beaten < len(TOURNAMENT_OPPONENTS):
            module = __import__(
                "src.scenes.tournament_scene",
                fromlist=["TournamentScene"],
            )
            scene_class = getattr(module, "TournamentScene")
            return scene_class(self.game)

        return MenuScene(self.game)

    def _draw_background(self, surface: pygame.Surface) -> None:
        court_rect = pygame.Rect(120, 150, WIDTH - 240, HEIGHT - 230)
        pygame.draw.rect(surface, WHITE, court_rect, width=5, border_radius=22)
        pygame.draw.line(
            surface,
            WHITE,
            (court_rect.left, court_rect.centery),
            (court_rect.right, court_rect.centery),
            5,
        )
        pygame.draw.circle(surface, WHITE, (84, HEIGHT - 76), 28)
        pygame.draw.circle(surface, BLACK, (84, HEIGHT - 76), 28, width=4)

    def _draw_result_details(self, surface: pygame.Surface) -> None:
        winner_text = self._body_font.render(
            f"Vencedor: {self.winner_name}",
            True,
            BLACK,
        )
        surface.blit(winner_text, winner_text.get_rect(center=(WIDTH // 2, 170)))

        progress_text = self._progress_text()
        rendered = self._small_font.render(progress_text, True, BLACK)
        surface.blit(rendered, rendered.get_rect(center=(WIDTH // 2, 214)))

    def _draw_animated_trophy(self, surface: pygame.Surface) -> None:
        trophy = self.game.assets.get("trophy", make_trophy)
        elapsed = pygame.time.get_ticks() / 180
        trophy_y = 328 + round(math.sin(elapsed) * 10)
        surface.blit(trophy, trophy.get_rect(center=(WIDTH // 2, trophy_y)))

    def _draw_return_button(self, surface: pygame.Surface) -> None:
        label = "CONTINUAR"
        button = self.game.assets.get(
            ("button", label, BLUE, 250, 54),
            lambda: make_button(label, BLUE, 250, 54),
        )
        surface.blit(button, button.get_rect(center=(WIDTH // 2, HEIGHT - 78)))

    def _draw_outlined_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        center: tuple[int, int],
    ) -> None:
        text_rect = font.render(text, True, WHITE).get_rect(center=center)
        for offset_x, offset_y in ((-4, 0), (4, 0), (0, -4), (0, 4)):
            outline = font.render(text, True, BLACK)
            surface.blit(outline, text_rect.move(offset_x, offset_y))

        rendered = font.render(text, True, WHITE)
        surface.blit(rendered, text_rect)

    def _progress_text(self) -> str:
        if self.mode == "1p":
            total = len(TOURNAMENT_OPPONENTS)
            return f"Torneio: {self.opponents_beaten}/{total} adversarios vencidos"

        if self.mode == "2p":
            return "Partida local encerrada"

        return "Treino encerrado"
