"""Cena de selecao de personagem antes do inicio de uma partida."""

from __future__ import annotations

import os

import pygame

from src.scenes.base_scene import BaseScene
from src.settings import BLACK, BLUE, HEIGHT, ORANGE, WHITE, WIDTH, YELLOW

CHARACTERS = [
    {"id": "borger", "name": "Borger", "sprite": "Borger.png"},
    {"id": "dudi", "name": "Dudi", "sprite": "Dudi.png"},
    {"id": "pacheco", "name": "Pacheco", "sprite": "Pacheco.png"},
]

CARD_W = 300
CARD_H = 400
CARD_GAP = 50
IMG_AREA_H = 310
CARD_TOP_Y = 160


class CharacterSelectionScene(BaseScene):
    """Exibe painel de selecao de personagem para um ou dois jogadores.

    Args:
        game: Instancia principal do jogo.
        mode: Modo de jogo escolhido no menu ("tournament", "2p" ou "training").
    """

    def __init__(self, game, mode: str) -> None:
        super().__init__(game)
        self.mode = mode
        self.selected_index = 0
        self._next_scene = None
        self._selecting_player = 1
        self._p1_choice: dict | None = None

        self._title_font = pygame.font.Font(None, 62)
        self._player_font = pygame.font.Font(None, 44)
        self._name_font = pygame.font.Font(None, 46)
        self._hint_font = pygame.font.Font(None, 30)

        self._sprites = self._load_sprites()

    def _load_sprites(self) -> list[pygame.Surface]:
        sprites = []
        sprites_dir = os.path.join("assets", "sprites")
        for char in CHARACTERS:
            path = os.path.join(sprites_dir, char["sprite"])
            try:
                img = pygame.image.load(path).convert_alpha()
            except Exception:
                fallback = pygame.Surface((200, 280), pygame.SRCALPHA)
                fallback.fill(BLUE)
                img = fallback
            sprites.append(img)
        return sprites

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from src.scenes.menu_scene import MenuScene
                self._next_scene = MenuScene(self.game)
            elif event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(CHARACTERS)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(CHARACTERS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._confirm_selection()

    def _confirm_selection(self) -> None:
        chosen = CHARACTERS[self.selected_index]

        if self.mode == "2p" and self._selecting_player == 1:
            self._p1_choice = chosen
            self._selecting_player = 2
            self.selected_index = 0
            return

        if self.mode == "2p":
            self.game.player1_character = self._p1_choice
            self.game.player2_character = chosen
            self._next_scene = self._build_match_format("2p")
        elif self.mode == "training":
            self.game.player1_character = chosen
            self.game.player2_character = None
            self._next_scene = self._build_gameplay("training")
        else:
            self.game.player1_character = chosen
            self._next_scene = self._build_match_format("tournament")

    def _build_gameplay(self, mode: str) -> object:
        from src.scenes.gameplay_scene import GameplayScene
        return GameplayScene(self.game, mode=mode)

    def _build_match_format(self, mode: str) -> object:
        from src.scenes.match_format_scene import MatchFormatScene
        return MatchFormatScene(self.game, mode=mode)

    def _build_tournament(self) -> object:
        from src.scenes.tournament_scene import TournamentScene
        return TournamentScene(self.game)

    def update(self, dt: float) -> None:
        pass

    def next_scene(self) -> object:
        ns = self._next_scene
        self._next_scene = None
        return ns

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(YELLOW)
        self._draw_background_court(surface)
        self._draw_title(surface)
        self._draw_player_indicator(surface)
        self._draw_cards(surface)
        self._draw_hint(surface)

    def _draw_background_court(self, surface: pygame.Surface) -> None:
        court_rect = pygame.Rect(80, 100, WIDTH - 160, HEIGHT - 150)
        pygame.draw.rect(surface, WHITE, court_rect, width=4, border_radius=20)

    def _draw_title(self, surface: pygame.Surface) -> None:
        title = "ESCOLHA SEU PERSONAGEM"
        offsets = [(-3, 0), (3, 0), (0, -3), (0, 3)]
        center = (WIDTH // 2, 62)
        for dx, dy in offsets:
            surf = self._title_font.render(title, True, BLACK)
            rect = surf.get_rect(center=center)
            surface.blit(surf, rect.move(dx, dy))
        surf = self._title_font.render(title, True, WHITE)
        surface.blit(surf, surf.get_rect(center=center))

    def _draw_player_indicator(self, surface: pygame.Surface) -> None:
        if self.mode != "2p":
            return
        label = f"JOGADOR {self._selecting_player}"
        color = ORANGE if self._selecting_player == 1 else BLUE
        surf = self._player_font.render(label, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, 118))
        pygame.draw.rect(
            surface,
            color,
            rect.inflate(24, 10),
            width=3,
            border_radius=8,
        )
        surface.blit(surf, rect)

    def _draw_cards(self, surface: pygame.Surface) -> None:
        total_w = len(CHARACTERS) * CARD_W + (len(CHARACTERS) - 1) * CARD_GAP
        start_x = (WIDTH - total_w) // 2

        for i, (char, sprite) in enumerate(zip(CHARACTERS, self._sprites)):
            x = start_x + i * (CARD_W + CARD_GAP)
            is_selected = i == self.selected_index
            self._draw_single_card(surface, char, sprite, x, CARD_TOP_Y, is_selected)

    def _draw_single_card(
        self,
        surface: pygame.Surface,
        char: dict,
        sprite: pygame.Surface,
        x: int,
        y: int,
        is_selected: bool,
    ) -> None:
        card_rect = pygame.Rect(x, y, CARD_W, CARD_H)
        bg_color = (255, 240, 195) if is_selected else (210, 228, 255)
        border_color = ORANGE if is_selected else WHITE
        border_w = 7 if is_selected else 3

        pygame.draw.rect(surface, bg_color, card_rect, border_radius=18)
        pygame.draw.rect(surface, border_color, card_rect, width=border_w, border_radius=18)

        img_area = pygame.Rect(x + 12, y + 12, CARD_W - 24, IMG_AREA_H)
        scale = min(img_area.width / sprite.get_width(), img_area.height / sprite.get_height())
        new_w = int(sprite.get_width() * scale)
        new_h = int(sprite.get_height() * scale)
        scaled = pygame.transform.scale(sprite, (new_w, new_h))
        img_x = x + (CARD_W - new_w) // 2
        img_y = y + 12 + (IMG_AREA_H - new_h) // 2
        surface.blit(scaled, (img_x, img_y))

        name_color = ORANGE if is_selected else BLACK
        name_surf = self._name_font.render(char["name"].upper(), True, name_color)
        name_rect = name_surf.get_rect(center=(x + CARD_W // 2, y + CARD_H - 38))
        surface.blit(name_surf, name_rect)

        if is_selected:
            arrow = self._name_font.render("▼", True, ORANGE)
            arrow_rect = arrow.get_rect(center=(x + CARD_W // 2, y + CARD_H + 22))
            surface.blit(arrow, arrow_rect)

    def _draw_hint(self, surface: pygame.Surface) -> None:
        hint = "← → Navegar     ENTER Selecionar     ESC Voltar"
        surf = self._hint_font.render(hint, True, BLACK)
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT - 28))
        surface.blit(surf, rect)
