"""Cena de selecao do formato da partida (numero de games por set)."""

from __future__ import annotations

import pygame

from src.assets_generator import make_button
from src.scenes.base_scene import BaseScene
from src.settings import BLACK, BLUE, HEIGHT, ORANGE, WHITE, WIDTH, YELLOW


_OPTIONS = [
    {"label": "3 games vence", "games": 3},
    {"label": "6 games vence", "games": 6},
]


class MatchFormatScene(BaseScene):
    """Pergunta ao jogador quantos games sao necessarios para vencer o set.

    Args:
        game: Instancia principal do jogo.
        mode: Modo de jogo escolhido (``"tournament"`` ou ``"2p"``).

    Attributes:
        selected_index: Indice da opcao atualmente destacada.
    """

    def __init__(self, game, mode: str) -> None:
        """Inicializa a cena com o primeiro formato selecionado por padrao."""
        super().__init__(game)
        self.mode = mode
        self.selected_index = 1  # padrão: 6 games
        self._next_scene = None
        self._title_font = pygame.font.Font(None, 68)
        self._sub_font = pygame.font.Font(None, 36)
        self._hint_font = pygame.font.Font(None, 28)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa navegacao por teclado e confirmacao da escolha.

        Args:
            events: Lista de eventos capturados pelo Pygame neste quadro.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from src.scenes.character_selection_scene import CharacterSelectionScene
                self._next_scene = CharacterSelectionScene(self.game, mode=self.mode)
            elif event.key in (pygame.K_UP, pygame.K_LEFT):
                self.selected_index = (self.selected_index - 1) % len(_OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.selected_index = (self.selected_index + 1) % len(_OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._confirm()

    def _confirm(self) -> None:
        option = _OPTIONS[self.selected_index]
        self.game.games_target_set = option["games"]

        if self.mode == "tournament":
            from src.scenes.tournament_scene import TournamentScene
            self._next_scene = TournamentScene(self.game)
        else:
            from src.scenes.gameplay_scene import GameplayScene
            self._next_scene = GameplayScene(self.game, mode="2p")

    def update(self, dt: float) -> None:
        """Mantém a cena estatica.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha o painel de selecao do formato da partida.

        Args:
            surface: Superficie principal onde a cena deve ser desenhada.
        """
        surface.fill(YELLOW)
        self._draw_background_court(surface)
        self._draw_title(surface)
        self._draw_subtitle(surface)
        self._draw_buttons(surface)
        self._draw_hint(surface)

    def next_scene(self) -> object:
        """Retorna a proxima cena apos a confirmacao do formato.

        Returns:
            Proxima cena escolhida, ou None enquanto aguarda confirmacao.
        """
        ns = self._next_scene
        self._next_scene = None
        return ns

    def _draw_background_court(self, surface: pygame.Surface) -> None:
        court_rect = pygame.Rect(110, 110, WIDTH - 220, HEIGHT - 160)
        pygame.draw.rect(surface, WHITE, court_rect, width=5, border_radius=18)

    def _draw_title(self, surface: pygame.Surface) -> None:
        title = "FORMATO DA PARTIDA"
        offsets = [(-3, 0), (3, 0), (0, -3), (0, 3)]
        center = (WIDTH // 2, 72)
        for dx, dy in offsets:
            surf = self._title_font.render(title, True, BLACK)
            rect = surf.get_rect(center=center)
            surface.blit(surf, rect.move(dx, dy))
        surf = self._title_font.render(title, True, WHITE)
        surface.blit(surf, surf.get_rect(center=center))

    def _draw_subtitle(self, surface: pygame.Surface) -> None:
        sub = "Quantos games sao necessarios para vencer um set?"
        surf = self._sub_font.render(sub, True, BLACK)
        rect = surf.get_rect(center=(WIDTH // 2, 148))
        surface.blit(surf, rect)

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        button_w = 420
        button_h = 72
        gap = 28
        total_h = len(_OPTIONS) * button_h + (len(_OPTIONS) - 1) * gap
        start_y = HEIGHT // 2 - total_h // 2

        for i, option in enumerate(_OPTIONS):
            color = ORANGE if i == self.selected_index else BLUE
            btn = self.game.assets.get(
                ("match_fmt_btn", option["label"], color, button_w, button_h),
                lambda lbl=option["label"], c=color: make_button(lbl, c, button_w, button_h),
            )
            rect = btn.get_rect(center=(WIDTH // 2, start_y + i * (button_h + gap) + button_h // 2))
            surface.blit(btn, rect)

    def _draw_hint(self, surface: pygame.Surface) -> None:
        hint = "Setas para navegar  |  ENTER para confirmar  |  ESC Voltar"
        surf = self._hint_font.render(hint, True, BLACK)
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT - 34))
        surface.blit(surf, rect)
