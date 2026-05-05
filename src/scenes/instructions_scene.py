"""Cena de instrucoes e controles do jogo."""

from __future__ import annotations

import pygame

from src.scenes.base_scene import BaseScene
from src.scenes.menu_scene import MenuScene
from src.settings import (
    BAR_HEIGHT,
    BAR_WIDTH,
    BLACK,
    BLUE,
    GRAY_LIGHT,
    GREEN_SWEET,
    HEIGHT,
    LINE_OUTLINE,
    ORANGE,
    WHITE,
    WIDTH,
    YELLOW,
)


class InstructionsScene(BaseScene):
    """Explica controles, barras sequenciais e pontuacao.

    Args:
        game: Instancia principal do jogo usada para voltar ao menu.
    """

    TEXT_LINES = (
        "Controles do Player 1",
        "← → ↑ ↓ movem o jogador pelo proprio campo.",
        "ESPAÇO trava as barras: primeiro angulo, depois forca.",
        "",
        "1. Quando a bola se aproxima, a BARRA DE ÂNGULO aparece e oscila.",
        "Pressione ESPAÇO para travar a direção.",
        "2. Em seguida a BARRA DE FORÇA oscila.",
        "Acerte na zona VERDE para um winner e pressione ESPAÇO de novo.",
        "",
        "Pontuação oficial: 0, 15, 30, 40, game, sets e tie-break em 6-6.",
    )

    def __init__(self, game) -> None:
        """Inicializa fontes e estado de transicao."""
        super().__init__(game)
        self._next_scene = None
        self._title_font = pygame.font.Font(None, 66)
        self._body_font = pygame.font.Font(None, 30)
        self._strong_font = pygame.font.Font(None, 34)
        self._strong_font.set_bold(True)
        self._hint_font = pygame.font.Font(None, 26)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Volta ao menu quando ENTER ou ESC sao pressionados.

        Args:
            events: Lista de eventos capturados pelo Pygame neste quadro.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                self._next_scene = MenuScene(self.game)

    def update(self, dt: float) -> None:
        """Mantem a tela informativa estatica.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha titulo, texto centralizado e barras demonstrativas.

        Args:
            surface: Superficie principal onde a cena deve ser desenhada.
        """
        surface.fill(YELLOW)
        self._draw_background(surface)
        self._draw_title(surface)
        self._draw_text(surface)
        self._draw_bar_demo(surface)
        self._draw_hint(surface)

    def next_scene(self):
        """Retorna a cena de menu quando solicitada.

        Returns:
            MenuScene quando o usuario sai da tela, ou None para permanecer.
        """
        next_scene = self._next_scene
        self._next_scene = None
        return next_scene

    def _draw_background(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(70, 100, WIDTH - 140, HEIGHT - 165)
        pygame.draw.rect(surface, WHITE, panel, border_radius=18)
        pygame.draw.rect(surface, BLACK, panel, width=5, border_radius=18)
        pygame.draw.circle(surface, BLUE, (86, 82), 28)
        pygame.draw.circle(surface, BLACK, (86, 82), 28, width=4)
        pygame.draw.circle(surface, ORANGE, (WIDTH - 86, 82), 28)
        pygame.draw.circle(surface, BLACK, (WIDTH - 86, 82), 28, width=4)

    def _draw_title(self, surface: pygame.Surface) -> None:
        self._draw_outlined_text(
            surface,
            "COMO JOGAR",
            self._title_font,
            (WIDTH // 2, 63),
            WHITE,
        )

    def _draw_text(self, surface: pygame.Surface) -> None:
        y = 126
        for line in self.TEXT_LINES:
            if not line:
                y += 12
                continue

            font = (
                self._strong_font
                if line.startswith("Controles")
                else self._body_font
            )
            color = BLACK
            text = font.render(line, True, color)
            rect = text.get_rect(center=(WIDTH // 2, y))
            surface.blit(text, rect)
            y += 32

    def _draw_bar_demo(self, surface: pygame.Surface) -> None:
        base_x = (WIDTH - BAR_WIDTH) // 2
        angle_y = 424
        power_y = angle_y + 46
        self._draw_demo_bar(surface, base_x, angle_y, "ÂNGULO", 0.66, ORANGE)
        self._draw_demo_bar(surface, base_x, power_y, "FORÇA", 0.78, GREEN_SWEET)

        sweet_start = base_x + int(BAR_WIDTH * 0.70)
        sweet_width = int(BAR_WIDTH * 0.20)
        sweet_rect = pygame.Rect(sweet_start, power_y, sweet_width, BAR_HEIGHT)
        pygame.draw.rect(surface, GREEN_SWEET, sweet_rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, sweet_rect, width=2, border_radius=8)
        self._draw_cursor(surface, base_x, power_y, 0.78, GREEN_SWEET)

    def _draw_demo_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        label: str,
        cursor_ratio: float,
        cursor_color: tuple[int, int, int],
    ) -> None:
        label_text = self._strong_font.render(label, True, BLACK)
        label_rect = label_text.get_rect(center=(x - 72, y + BAR_HEIGHT // 2))
        surface.blit(label_text, label_rect)

        rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, LINE_OUTLINE, rect, border_radius=8)
        inner = rect.inflate(-6, -6)
        pygame.draw.rect(surface, GRAY_LIGHT, inner, border_radius=6)
        self._draw_cursor(surface, x, y, cursor_ratio, cursor_color)

    def _draw_cursor(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        ratio: float,
        color: tuple[int, int, int],
    ) -> None:
        cursor_x = x + int(BAR_WIDTH * ratio)
        cursor_rect = pygame.Rect(cursor_x - 5, y - 6, 10, BAR_HEIGHT + 12)
        pygame.draw.rect(surface, BLACK, cursor_rect, border_radius=5)
        pygame.draw.rect(surface, color, cursor_rect.inflate(-4, -4), border_radius=4)

    def _draw_hint(self, surface: pygame.Surface) -> None:
        hint = self._hint_font.render("ENTER ou ESC para voltar ao menu", True, BLACK)
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

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
