"""Bot simples para o modo treino."""

from __future__ import annotations

import random

import pygame
from pygame.math import Vector2

from src.assets_generator import make_ai_sprites
from src.settings import (
    COURT_MARGIN_X,
    COURT_MARGIN_Y,
    HEIGHT,
    HIT_RADIUS,
    PLAYER_WIDTH,
    WIDTH,
)
from src.utils.asset_cache import AssetCache


class PracticeBot(pygame.sprite.Sprite):
    """Rebatedor automatico usado no treino sem placar."""

    def __init__(self, asset_cache: AssetCache) -> None:
        """Inicializa o bot na metade direita da quadra."""
        super().__init__()
        self.side = "right"
        self.name = "Bot Treino"
        self.speed = 250
        sprites = asset_cache.get(
            ("practice_bot_sprites", "forest"),
            lambda: make_ai_sprites("forest"),
        )
        self._sprite_idle, self._sprite_run = sprites
        self.image = self._sprite_idle
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = Vector2(WIDTH - COURT_MARGIN_X - PLAYER_WIDTH // 2, HEIGHT / 2)
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self._anim_timer = 0.0
        self._anim_frame = 0
        self._is_moving = False

    def update(self, dt: float, ball) -> str:
        """Move em direcao a bola e rebate quando ela esta perto."""
        self._is_moving = False
        self._follow_ball(dt, ball)
        self._update_animation(dt)
        if self._can_hit(ball) and ball.velocity.x > 0:
            angle = random.uniform(-30, 30)
            ball.apply_shot(angle, 0.6, self.side, False)
            ball.last_hitter = self.side
            ball.bounce_count = 0
            return "normal"

        return "no_hit"

    def _update_animation(self, dt: float) -> None:
        if self._is_moving:
            self._anim_timer += dt
            if self._anim_timer >= 0.10:
                self._anim_timer -= 0.10
                self._anim_frame ^= 1
            self.image = self._sprite_run if self._anim_frame else self._sprite_idle
        else:
            self._anim_frame = 0
            self._anim_timer = 0.0
            self.image = self._sprite_idle

    def _follow_ball(self, dt: float, ball) -> None:
        target_y = ball.pos.y
        max_step = self.speed * dt
        distance = target_y - self.pos.y

        if abs(distance) <= max_step:
            self.pos.y = target_y
        else:
            self.pos.y += max_step if distance > 0 else -max_step
            self._is_moving = True

        half_height = self.rect.height / 2
        self.pos.y = max(
            COURT_MARGIN_Y + half_height,
            min(HEIGHT - COURT_MARGIN_Y - half_height, self.pos.y),
        )
        self.pos.x = WIDTH - COURT_MARGIN_X - PLAYER_WIDTH // 2
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def _can_hit(self, ball) -> bool:
        bot_center = Vector2(self.rect.center)
        ball_center = Vector2(ball.rect.center)
        return bot_center.distance_to(ball_center) <= HIT_RADIUS
