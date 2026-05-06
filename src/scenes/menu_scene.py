"""Cena de menu principal do jogo."""

from __future__ import annotations

import pygame

from src.assets_generator import make_button
from src.scenes.base_scene import BaseScene
from src.settings import BLACK, BLUE, HEIGHT, ORANGE, WHITE, WIDTH, YELLOW


class MenuScene(BaseScene):
    """Exibe o menu principal com as opcoes de jogo.

    Args:
        game: Instancia principal do jogo, usada para trocar cenas e encerrar
            a aplicacao.

    Attributes:
        selected_index: Indice da opcao atualmente selecionada.
    """

    OPTIONS = (
        "Torneio (1P vs CPU)",
        "2 Jogadores Local",
        "Modo Treino",
        "Como Jogar",
        "Recordes",
        "Sair",
    )

    def __init__(self, game) -> None:
        """Inicializa o menu na primeira opcao."""
        super().__init__(game)
        self.selected_index = 0
        self._next_scene = None
        self._title_font = pygame.font.Font(None, 82)
        self._hint_font = pygame.font.Font(None, 28)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa navegacao do menu por teclado.

        Args:
            events: Lista de eventos capturados pelo Pygame neste quadro.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.OPTIONS)
                self._play_sound("menu_click")
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.OPTIONS)
                self._play_sound("menu_click")
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._play_sound("menu_click")
                self._activate_selected_option()

    def update(self, dt: float) -> None:
        """Mantem o menu estatico.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha fundo, titulo e botoes do menu.

        Args:
            surface: Superficie principal onde a cena deve ser desenhada.
        """
        surface.fill(YELLOW)
        self._draw_background_details(surface)
        self._draw_title(surface)
        self._draw_buttons(surface)

    def next_scene(self):
        """Retorna a proxima cena escolhida no menu.

        Returns:
            Cena selecionada, ou None quando o menu deve continuar ativo.
        """
        next_scene = self._next_scene
        self._next_scene = None
        return next_scene

    def _activate_selected_option(self) -> None:
        selected_option = self.OPTIONS[self.selected_index]

        if selected_option == "Sair":
            self.game.running = False
        elif selected_option == "Como Jogar":
            self._next_scene = self._build_scene("instructions_scene", "InstructionsScene")
        elif selected_option == "Torneio (1P vs CPU)":
            self._next_scene = self._build_scene("tournament_scene", "TournamentScene")
        elif selected_option == "2 Jogadores Local":
            self._next_scene = self._build_gameplay_scene("2p")
        elif selected_option == "Modo Treino":
            self._next_scene = self._build_gameplay_scene("training")
        else:
            self._next_scene = None

    def _build_scene(self, module_name: str, class_name: str):
        try:
            module = __import__(f"src.scenes.{module_name}", fromlist=[class_name])
        except ModuleNotFoundError:
            return None

        scene_class = getattr(module, class_name)
        return scene_class(self.game)

    def _build_gameplay_scene(self, mode: str):
        try:
            module = __import__("src.scenes.gameplay_scene", fromlist=["GameplayScene"])
        except ModuleNotFoundError:
            return None

        scene_class = getattr(module, "GameplayScene")
        return scene_class(self.game, mode=mode)

    def _play_sound(self, sound_name: str) -> None:
        sound_manager = getattr(self.game, "sound_manager", None)
        if sound_manager is not None:
            sound_manager.play(sound_name)

    def _draw_background_details(self, surface: pygame.Surface) -> None:
        court_rect = pygame.Rect(110, 120, WIDTH - 220, HEIGHT - 170)
        pygame.draw.rect(surface, WHITE, court_rect, width=5, border_radius=18)
        pygame.draw.line(
            surface,
            WHITE,
            (court_rect.left, court_rect.centery),
            (court_rect.right, court_rect.centery),
            5,
        )
        pygame.draw.circle(surface, ORANGE, (120, 92), 34)
        pygame.draw.circle(surface, BLACK, (120, 92), 34, width=4)

    def _draw_title(self, surface: pygame.Surface) -> None:
        title = "TENNIS CARTOON"
        outline_offsets = ((-3, 0), (3, 0), (0, -3), (0, 3))
        title_rect = self._title_font.render(title, True, WHITE).get_rect(
            center=(WIDTH // 2, 74)
        )

        for offset_x, offset_y in outline_offsets:
            outline = self._title_font.render(title, True, BLACK)
            surface.blit(outline, title_rect.move(offset_x, offset_y))

        text = self._title_font.render(title, True, WHITE)
        surface.blit(text, title_rect)

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        button_width = 390
        button_height = 54
        start_y = 150
        gap = 16

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
            rect = button.get_rect(
                center=(WIDTH // 2, start_y + index * (button_height + gap))
            )
            surface.blit(button, rect)

        hint = self._hint_font.render("Setas para navegar  ENTER para escolher", True, BLACK)
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 34))
        surface.blit(hint, hint_rect)
