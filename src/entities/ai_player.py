"""Jogador controlado por inteligencia artificial."""

from __future__ import annotations

import random

import pygame

from src.assets_generator import make_ai_sprites
from src.entities.player import Player
from src.settings import (
    AI_SPRITE_HEIGHT,
    AI_SPRITE_WIDTH,
    AIM_MAX_ANGLE,
    AIM_MIN_ANGLE,
    HEIGHT,
    NET_X,
    SWEET_SPOT_HIGH,
    SWEET_SPOT_LOW,
    WIDTH,
)
from src.utils.asset_cache import AssetCache


class AIPlayer(Player):
    """Representa um adversario controlado pela CPU.

    Args:
        asset_cache: Cache compartilhado para reutilizar assets gerados.
        side: Lado da quadra ocupado pela IA.
        opponent_config: Configuracao vinda de `TOURNAMENT_OPPONENTS`.

    Attributes:
        opponent_config: Dados de dificuldade, nome e visual do adversario.
        reaction_timer: Tempo restante ate a proxima decisao de alvo.
        target_y: Posicao vertical perseguida pela IA.
    """

    def __init__(
        self,
        asset_cache: AssetCache,
        side: str,
        opponent_config: dict,
    ) -> None:
        """Inicializa a IA com dificuldade definida pelo torneio."""
        super().__init__(asset_cache, side, controls={}, name=opponent_config["name"])
        self.opponent_config = opponent_config
        self.reaction_timer = 0.0
        self.target_y = self.pos.y

        opponent_id = opponent_config["id"]
        center = self.rect.center
        sprites = asset_cache.get(
            ("ai_sprites", opponent_id),
            lambda: make_ai_sprites(opponent_id),
        )
        self._sprite_idle, self._sprite_run = sprites
        self.image = self._sprite_idle
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        """Ignora entrada de teclado, pois a IA decide sozinha.

        Args:
            keys: Estado atual do teclado.
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """

    def decide(self, ball, dt: float) -> str:
        """Atualiza alvo, movimento e tentativa de rebatida da IA.

        Args:
            ball: Bola observada pela IA.
            dt: Tempo decorrido desde o ultimo quadro, em segundos.

        Returns:
            `"winner"` quando a forca sorteada cai no sweet spot, `"normal"`
            quando a IA rebate fora dele ou `"no_hit"` quando nao houve
            rebatida.
        """
        self.reaction_timer -= dt
        if self.reaction_timer <= 0:
            aim_error = self.opponent_config["aim_error"]
            self.target_y = ball.pos.y + random.uniform(-aim_error, aim_error)
            self.reaction_timer = self.opponent_config["reaction"]

        self._move_toward_target(dt)

        if self.can_hit(ball) and self._ball_is_approaching(ball):
            power = random.uniform(0.5, 1.0)
            angle = self._choose_shot_angle(ball)
            is_sweet = SWEET_SPOT_LOW <= power <= SWEET_SPOT_HIGH
            ball.apply_shot(angle, power, self.side, is_sweet)
            ball.last_hitter = self.side
            ball.bounce_count = 0
            return "winner" if is_sweet else "normal"

        return "no_hit"

    def update(self, dt: float, ball) -> str:
        """Atualiza a IA usando a bola como referencia.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
            ball: Bola usada para decisao de movimento e rebatida.

        Returns:
            Resultado textual da tentativa de rebatida.
        """
        self._is_moving = False
        result = self.decide(ball, dt)
        self._update_animation(dt)
        return result

    def _move_toward_target(self, dt: float) -> None:
        max_step = self.opponent_config["max_speed"] * dt
        distance = self.target_y - self.pos.y

        if abs(distance) <= max_step:
            self.pos.y = self.target_y
        else:
            self.pos.y += max_step if distance > 0 else -max_step

        if abs(distance) > 0:
            self._is_moving = True

        self._clamp_to_own_court()
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def _clamp_to_own_court(self) -> None:
        """Restringe a IA à própria metade da quadra sem cruzar a rede.

        Sobrescreve o metodo do pai para usar `AI_SPRITE_WIDTH`/`AI_SPRITE_HEIGHT`
        em vez de `PLAYER_WIDTH`/`PLAYER_HEIGHT`, ja que os sprites dos adversarios
        podem ter tamanho diferente do jogador humano.
        """
        half_w = AI_SPRITE_WIDTH / 2
        half_h = AI_SPRITE_HEIGHT / 2
        min_x = half_w
        max_x = WIDTH - half_w

        if self.side == "left":
            max_x = NET_X - half_w
        else:
            min_x = NET_X + half_w

        self.pos.x = max(min_x, min(max_x, self.pos.x))
        self.pos.y = max(half_h, min(HEIGHT - half_h, self.pos.y))

    def _choose_shot_angle(self, ball) -> float:
        base_angle = random.uniform(AIM_MIN_ANGLE, AIM_MAX_ANGLE)

        if ball.pos.y < HEIGHT / 2:
            return abs(base_angle)

        return -abs(base_angle)
