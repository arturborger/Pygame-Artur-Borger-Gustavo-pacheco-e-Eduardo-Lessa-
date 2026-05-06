"""Cena de pausa em overlay sobre o gameplay."""

from __future__ import annotations

import pygame

from src.assets_generator import make_button
from src.scenes.base_scene import BaseScene
from src.scenes.menu_scene import MenuScene
from src.settings import BLACK, BLUE, HEIGHT, LINE_OUTLINE, ORANGE, WHITE, WIDTH


class PauseScene(BaseScene):
    """Exibe um menu de pausa mantendo a partida congelada ao fundo.

    Args:
        game: Instância principal do jogo.
        previous_scene: Cena de gameplay que deve ser retomada ao continuar.

    Attributes:
        previous_scene: Referência para a partida pausada.
        selected_index: Índice do botão selecionado.
    """

    OPTIONS = ("CONTINUAR", "MENU PRINCIPAL")

    def __init__(self, game, previous_scene) -> None:
        """Inicializa o overlay com a opção continuar selecionada."""
        super().__init__(game)
        self.previous_scene = previous_scene
        self.selected_index = 0
        self._next_scene = None
        self._title_font = pygame.font.Font(None, 62)
        self._title_font.set_bold(True)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa navegação do menu de pausa.

        Args:
            events: Lista de eventos capturados no quadro atual.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self._next_scene = self.previous_scene
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.OPTIONS)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._activate_selected_option()

    def update(self, dt: float) -> None:
        """Mantém o jogo pausado sem atualizar a partida.

        Args:
            dt: Tempo decorrido desde o último quadro, ignorado nesta cena.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha a partida congelada e o painel de pausa.

        Args:
            surface: Superfície principal onde a cena deve renderizar.
        """
        self.previous_scene.draw(surface)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        self._draw_panel(surface)

    def next_scene(self):
        """Retorna a cena escolhida no menu de pausa.

        Returns:
            A partida anterior, o menu principal ou ``None``.
        """
        next_scene = self._next_scene
        self._next_scene = None
        return next_scene

    def _activate_selected_option(self) -> None:
        selected_option = self.OPTIONS[self.selected_index]
        if selected_option == "CONTINUAR":
            self._next_scene = self.previous_scene
        else:
            self._stop_music()
            self._next_scene = MenuScene(self.game)

    def _stop_music(self) -> None:
        sound_manager = getattr(self.game, "sound_manager", None)
        if sound_manager is None:
            return

        stop_music = getattr(sound_manager, "stop_music", None)
        if callable(stop_music):
            stop_music()

    def _draw_panel(self, surface: pygame.Surface) -> None:
        panel_rect = pygame.Rect(0, 0, 360, 260)
        panel_rect.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(surface, WHITE, panel_rect, border_radius=14)
        pygame.draw.rect(
            surface,
            LINE_OUTLINE,
            panel_rect,
            width=5,
            border_radius=14,
        )

        title = self._title_font.render("PAUSA", True, BLACK)
        title_rect = title.get_rect(center=(panel_rect.centerx, panel_rect.top + 56))
        surface.blit(title, title_rect)
        self._draw_buttons(surface, panel_rect)

    def _draw_buttons(self, surface: pygame.Surface, panel_rect: pygame.Rect) -> None:
        button_width = 250
        button_height = 52
        start_y = panel_rect.top + 108
        gap = 22

        for index, option in enumerate(self.OPTIONS):
            color = ORANGE if index == self.selected_index else BLUE
            button = self.game.assets.get(
                ("button", option, color, button_width, button_height),
                lambda option=option, color=color: make_button(
                    option,
                    color,
                    button_width,
                    button_height,
                ),
            )
            button_rect = button.get_rect(
                center=(
                    panel_rect.centerx,
                    start_y + index * (button_height + gap),
                )
            )
            surface.blit(button, button_rect)
