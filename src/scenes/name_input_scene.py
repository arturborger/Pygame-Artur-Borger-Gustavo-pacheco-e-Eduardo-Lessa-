"""Cena de entrada do nome do jogador antes do inicio de uma partida."""

from __future__ import annotations

import pygame

from src.scenes.base_scene import BaseScene
from src.settings import BLACK, BLUE, HEIGHT, ORANGE, WHITE, WIDTH, YELLOW

_MAX_NAME_LEN = 16
_MIN_NAME_LEN = 1


class NameInputScene(BaseScene):
    """Solicita o nome do jogador antes de iniciar a selecao de personagem.

    Args:
        game: Instancia principal do jogo.
        mode: Modo de jogo escolhido no menu (``"tournament"``, ``"2p"`` ou
            ``"training"``).

    Attributes:
        mode: Modo de jogo que sera repassado apos confirmacao.
    """

    def __init__(self, game, mode: str) -> None:
        """Inicializa a cena com o campo de nome vazio."""
        super().__init__(game)
        self.mode = mode
        self._name: str = ""
        self._next_scene = None
        self._cursor_visible = True
        self._cursor_timer = 0.0
        self._show_error = False
        self._title_font = pygame.font.Font(None, 72)
        self._input_font = pygame.font.Font(None, 60)
        self._hint_font = pygame.font.Font(None, 30)
        self._error_font = pygame.font.Font(None, 30)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa entrada de teclado para o nome do jogador.

        Args:
            events: Lista de eventos capturados pelo Pygame neste quadro.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from src.scenes.menu_scene import MenuScene
                self._next_scene = MenuScene(self.game)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._confirm()
            elif event.key == pygame.K_BACKSPACE:
                self._name = self._name[:-1]
                self._show_error = False
            else:
                char = event.unicode
                if char and char.isprintable() and len(self._name) < _MAX_NAME_LEN:
                    self._name += char
                    self._show_error = False

    def update(self, dt: float) -> None:
        """Atualiza o cursor piscante.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:
            self._cursor_visible = not self._cursor_visible
            self._cursor_timer = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha o campo de entrada do nome do jogador.

        Args:
            surface: Superficie principal onde a cena deve ser desenhada.
        """
        surface.fill(YELLOW)
        self._draw_background(surface)
        self._draw_title(surface)
        self._draw_input_box(surface)
        self._draw_hint(surface)
        if self._show_error:
            self._draw_error(surface)

    def next_scene(self) -> object:
        """Retorna a proxima cena apos confirmacao do nome.

        Returns:
            CharacterSelectionScene ou MenuScene, conforme a acao do usuario.
        """
        ns = self._next_scene
        self._next_scene = None
        return ns

    def _confirm(self) -> None:
        """Valida e confirma o nome digitado, avanando para selecao de personagem."""
        name = self._name.strip()
        if len(name) < _MIN_NAME_LEN:
            self._show_error = True
            return

        self.game.player_name = name
        if self.mode == "tournament":
            self.game.tournament_progress = 0
            self.game.tournament_time_ms = 0

        from src.scenes.character_selection_scene import CharacterSelectionScene
        self._next_scene = CharacterSelectionScene(self.game, mode=self.mode)

    def _draw_background(self, surface: pygame.Surface) -> None:
        court_rect = pygame.Rect(110, 110, WIDTH - 220, HEIGHT - 160)
        pygame.draw.rect(surface, WHITE, court_rect, width=5, border_radius=18)
        pygame.draw.circle(surface, ORANGE, (148, 88), 36)
        pygame.draw.circle(surface, BLACK, (148, 88), 36, width=4)
        pygame.draw.circle(surface, BLUE, (WIDTH - 148, 88), 36)
        pygame.draw.circle(surface, BLACK, (WIDTH - 148, 88), 36, width=4)

    def _draw_title(self, surface: pygame.Surface) -> None:
        title = "QUAL E O SEU NOME?"
        offsets = [(-3, 0), (3, 0), (0, -3), (0, 3)]
        center = (WIDTH // 2, 76)
        for dx, dy in offsets:
            surf = self._title_font.render(title, True, BLACK)
            surface.blit(surf, surf.get_rect(center=center).move(dx, dy))
        surf = self._title_font.render(title, True, WHITE)
        surface.blit(surf, surf.get_rect(center=center))

    def _draw_input_box(self, surface: pygame.Surface) -> None:
        box_rect = pygame.Rect(0, 0, 600, 80)
        box_rect.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(surface, WHITE, box_rect, border_radius=14)
        pygame.draw.rect(surface, ORANGE, box_rect, width=6, border_radius=14)

        cursor = "|" if self._cursor_visible else " "
        display = self._name + cursor
        text_surf = self._input_font.render(display, True, BLACK)
        text_rect = text_surf.get_rect(center=box_rect.center)
        surface.blit(text_surf, text_rect)

    def _draw_hint(self, surface: pygame.Surface) -> None:
        hint = "Digite seu nome  |  ENTER para confirmar  |  ESC Voltar"
        surf = self._hint_font.render(hint, True, BLACK)
        surface.blit(surf, surf.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

    def _draw_error(self, surface: pygame.Surface) -> None:
        msg = "Digite pelo menos um caractere!"
        surf = self._error_font.render(msg, True, (200, 40, 40))
        surface.blit(surf, surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 66)))
