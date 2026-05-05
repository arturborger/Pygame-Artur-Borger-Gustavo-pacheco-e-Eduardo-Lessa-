"""Entidade do jogador humano."""

from __future__ import annotations

import pygame
from pygame.math import Vector2

from src.assets_generator import make_player_sprite
from src.settings import (
    BLUE,
    COURT_MARGIN,
    HEIGHT,
    NET_HEIGHT,
    NET_Y,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    RED,
    WIDTH,
)
from src.systems.timing_bars import TimingBars
from src.utils.asset_cache import AssetCache


class Player(pygame.sprite.Sprite):
    """Representa um jogador humano controlado pelo teclado.

    Args:
        asset_cache: Cache compartilhado para reutilizar superficies geradas.
        side: Lado da quadra ocupado pelo jogador, ``"bottom"`` ou ``"top"``.
        controls: Mapeamento das acoes para teclas Pygame.
        name: Nome exibido para o jogador.

    Attributes:
        image: Superficie do jogador obtida por `AssetCache`.
        rect: Retangulo usado para posicionamento e colisao.
        mask: Mascara para colisao precisa.
        side: Lado da quadra ocupado pelo jogador.
        controls: Mapeamento de teclas do jogador.
        name: Nome exibido para o jogador.
        timing_bars: Barras sequenciais de mira e forca.
        aim_state: Estado textual auxiliar da mira.
        pos: Posicao central do jogador em ponto flutuante.
    """

    def __init__(
        self,
        asset_cache: AssetCache,
        side: str,
        controls: dict[str, int],
        name: str = "Jogador",
    ) -> None:
        """Inicializa o jogador na metade correspondente da quadra."""
        super().__init__()
        self.side = side
        self.controls = controls
        self.name = name
        self.aim_state = "IDLE"

        color = BLUE if side == "bottom" else RED
        self.image = asset_cache.get(
            ("player_sprite", side, color),
            lambda: make_player_sprite(color),
        )
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        start_y = (
            HEIGHT - COURT_MARGIN - PLAYER_HEIGHT // 2
            if side == "bottom"
            else COURT_MARGIN + PLAYER_HEIGHT // 2
        )
        self.pos = Vector2(WIDTH / 2, start_y)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        lock_key = controls.get("lock", pygame.K_SPACE)
        self.timing_bars = TimingBars(side, lock_key)

    def handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        """Move o jogador conforme as teclas pressionadas.

        Args:
            keys: Estado atual do teclado retornado por `pygame.key.get_pressed`.
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """
        direction = Vector2()

        if keys[self.controls.get("left", pygame.K_LEFT)]:
            direction.x -= 1
        if keys[self.controls.get("right", pygame.K_RIGHT)]:
            direction.x += 1
        if keys[self.controls.get("up", pygame.K_UP)]:
            direction.y -= 1
        if keys[self.controls.get("down", pygame.K_DOWN)]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.pos += direction * PLAYER_SPEED * dt
            self._clamp_to_own_court()
            self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt: float) -> None:
        """Atualiza movimento e barras do jogador.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """
        keys = pygame.key.get_pressed()
        self.handle_input(keys, dt)
        self.timing_bars.update(dt)

    def _clamp_to_own_court(self) -> None:
        half_width = PLAYER_WIDTH / 2
        half_height = PLAYER_HEIGHT / 2
        min_x = COURT_MARGIN + half_width
        max_x = WIDTH - COURT_MARGIN - half_width

        if self.side == "bottom":
            min_y = NET_Y + NET_HEIGHT / 2 + half_height
            max_y = HEIGHT - COURT_MARGIN - half_height
        else:
            min_y = COURT_MARGIN + half_height
            max_y = NET_Y - NET_HEIGHT / 2 - half_height

        self.pos.x = max(min_x, min(max_x, self.pos.x))
        self.pos.y = max(min_y, min(max_y, self.pos.y))
