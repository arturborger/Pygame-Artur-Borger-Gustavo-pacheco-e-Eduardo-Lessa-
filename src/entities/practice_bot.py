"""Bot simples para o modo treino."""

from __future__ import annotations

import random

import pygame
from pygame.math import Vector2

from src.assets_generator import make_ai_sprite
from src.settings import COURT_MARGIN, HIT_RADIUS, PLAYER_HEIGHT, WIDTH
from src.utils.asset_cache import AssetCache


class PracticeBot(pygame.sprite.Sprite):
    """Rebatedor automatico usado no treino sem placar."""

    def __init__(self, asset_cache: AssetCache) -> None:
        """Inicializa o bot na metade superior da quadra."""
        super().__init__()
        self.side = "top"
        self.name = "Bot Treino"
        self.speed = 250
        self.image = asset_cache.get(
            ("practice_bot", "forest"),
            lambda: make_ai_sprite("forest"),
        )
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = Vector2(WIDTH / 2, COURT_MARGIN + PLAYER_HEIGHT // 2)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt: float, ball) -> str:
        """Move em direcao a bola e rebate quando ela esta perto."""
        self._follow_ball(dt, ball)
        if self._can_hit(ball) and ball.velocity.y < 0:
            angle = random.uniform(-30, 30)
            ball.apply_shot(angle, 0.6, self.side, False)
            ball.last_hitter = self.side
            ball.bounce_count = 0
            return "normal"

        return "no_hit"

    def _follow_ball(self, dt: float, ball) -> None:
        target_x = ball.pos.x
        max_step = self.speed * dt
        distance = target_x - self.pos.x

        if abs(distance) <= max_step:
            self.pos.x = target_x
        else:
            self.pos.x += max_step if distance > 0 else -max_step

        half_width = self.rect.width / 2
        self.pos.x = max(
            COURT_MARGIN + half_width,
            min(WIDTH - COURT_MARGIN - half_width, self.pos.x),
        )
        self.pos.y = COURT_MARGIN + PLAYER_HEIGHT // 2
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def _can_hit(self, ball) -> bool:
        bot_center = Vector2(self.rect.center)
        ball_center = Vector2(ball.rect.center)
        return bot_center.distance_to(ball_center) <= HIT_RADIUS
