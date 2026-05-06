"""Bot simples para o modo treino."""

from __future__ import annotations

import random

import pygame
from pygame.math import Vector2

from src.assets_generator import make_ai_sprite
from src.settings import COURT_MARGIN, HEIGHT, HIT_RADIUS, PLAYER_WIDTH, WIDTH
from src.utils.asset_cache import AssetCache


class PracticeBot(pygame.sprite.Sprite):
    """Rebatedor automatico usado no treino sem placar."""

    def __init__(self, asset_cache: AssetCache) -> None:
        """Inicializa o bot na metade direita da quadra."""
        super().__init__()
        self.side = "right"
        self.name = "Bot Treino"
        self.speed = 250
        self.image = asset_cache.get(
            ("practice_bot", "forest"),
            lambda: make_ai_sprite("forest"),
        )
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = Vector2(WIDTH - COURT_MARGIN - PLAYER_WIDTH // 2, HEIGHT / 2)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt: float, ball) -> str:
        """Move em direcao a bola e rebate quando ela esta perto."""
        self._follow_ball(dt, ball)
        if self._can_hit(ball) and ball.velocity.x > 0:
            angle = random.uniform(-30, 30)
            ball.apply_shot(angle, 0.6, self.side, False)
            ball.last_hitter = self.side
            ball.bounce_count = 0
            return "normal"

        return "no_hit"

    def _follow_ball(self, dt: float, ball) -> None:
        target_y = ball.pos.y
        max_step = self.speed * dt
        distance = target_y - self.pos.y

        if abs(distance) <= max_step:
            self.pos.y = target_y
        else:
            self.pos.y += max_step if distance > 0 else -max_step

        half_height = self.rect.height / 2
        self.pos.y = max(
            COURT_MARGIN + half_height,
            min(HEIGHT - COURT_MARGIN - half_height, self.pos.y),
        )
        self.pos.x = WIDTH - COURT_MARGIN - PLAYER_WIDTH // 2
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def _can_hit(self, ball) -> bool:
        bot_center = Vector2(self.rect.center)
        ball_center = Vector2(ball.rect.center)
        return bot_center.distance_to(ball_center) <= HIT_RADIUS
