"""Entidade da bola de tênis."""

from __future__ import annotations

import random
from math import cos, radians, sin

import pygame
from pygame.math import Vector2

from src.assets_generator import make_ball
from src.settings import (
    BALL_BASE_SPEED,
    BALL_MAX_SPEED,
    COURT_MARGIN,
    HEIGHT,
    MISS_JITTER,
    SWEET_SPOT_HIGH,
    SWEET_SPOT_LOW,
    WIDTH,
)
from src.utils.asset_cache import AssetCache


class Ball(pygame.sprite.Sprite):
    """Representa a bola do jogo e seu movimento básico.

    Attributes:
        image: Superfície da bola obtida pelo cache de assets.
        rect: Retângulo usado para posicionamento e colisões amplas.
        mask: Máscara da superfície usada para colisões precisas.
        pos: Posição central da bola em coordenadas de ponto flutuante.
        velocity: Velocidade atual da bola em pixels por segundo.
        last_hitter: Identificador do último lado que rebateu a bola.
        bounce_count: Quantidade de quicadas desde a última rebatida.
        was_served: Indica se o ponto ainda está no saque inicial.
        server_side: Lado do placar que sacou o ponto atual.
        last_hit_quality: Qualidade da última rebatida registrada.
        held_by_side: Lado do jogador humano que segurou a bola para mirar.
    """

    def __init__(
        self,
        asset_cache: AssetCache,
        start_pos: tuple[float, float] | pygame.math.Vector2,
    ) -> None:
        """Inicializa a bola na posição informada.

        Args:
            asset_cache: Cache compartilhado usado para reutilizar a imagem da bola.
            start_pos: Posição inicial do centro da bola, em pixels.
        """
        super().__init__()
        self.image = asset_cache.get("ball", make_ball)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = pygame.math.Vector2(start_pos)
        self.velocity = pygame.math.Vector2()
        self.last_hitter: str | None = None
        self.bounce_count = 0
        self.was_served = False
        self.server_side = "p1"
        self.last_hit_quality = "normal"
        self.held_by_side: str | None = None
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt: float) -> None:
        """Atualiza a posição da bola conforme sua velocidade.

        Args:
            dt: Tempo decorrido desde o último quadro, em segundos.
        """
        if not self.is_held():
            self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def capture_by_player(self, player) -> None:
        """Prende a bola ao jogador para a seleção de ângulo e força.

        Args:
            player: Jogador com atributos ``side`` e ``rect`` que segurará a
                bola até a rebatida.
        """
        self.held_by_side = player.side
        self.velocity.update(0, 0)
        self.follow_captured_player(player)

    def follow_captured_player(self, player) -> None:
        """Mantém a bola posicionada ao lado do jogador que a segurou.

        Args:
            player: Jogador que está controlando a mira da próxima rebatida.
        """
        if self.held_by_side != player.side:
            return

        ball_half_width = self.rect.width / 2
        if player.side == "left":
            x = player.rect.right + ball_half_width
        else:
            x = player.rect.left - ball_half_width

        self.pos.update(x, player.rect.centery)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def release(self) -> None:
        """Libera a bola do jogador que estava mirando a rebatida."""
        self.held_by_side = None

    def is_held(self) -> bool:
        """Indica se a bola está presa a algum jogador humano.

        Returns:
            ``True`` quando a bola está aguardando seleção de ângulo e força.
        """
        return self.held_by_side is not None

    def apply_shot(
        self,
        angle_deg: float,
        power: float,
        side_origin: str,
        is_sweet_spot: bool,
    ) -> bool:
        """Aplica uma rebatida calculando o novo vetor de velocidade.

        Args:
            angle_deg: Ângulo travado pela barra de mira, em graus.
            power: Força travada pela barra de força, entre 0 e 1.
            side_origin: Lado de origem da rebatida. Use ``"left"`` para a
                metade esquerda da quadra.
            is_sweet_spot: Indica se a rebatida já foi classificada como sweet
                spot pelo sistema de barras.

        Returns:
            ``True`` se a rebatida foi aplicada.
        """
        angle_locked = angle_deg
        power_locked = power

        if SWEET_SPOT_LOW <= power_locked <= SWEET_SPOT_HIGH:
            angle_jitter = 0
            is_sweet_spot = True
        else:
            angle_jitter = random.uniform(-MISS_JITTER, MISS_JITTER)
            is_sweet_spot = False

        final_angle = angle_locked + angle_jitter
        final_speed = BALL_BASE_SPEED + power_locked * (BALL_MAX_SPEED - BALL_BASE_SPEED)
        direction_x = 1 if side_origin == "left" else -1

        self.velocity = Vector2(
            cos(radians(final_angle)) * final_speed * direction_x,
            sin(radians(final_angle)) * final_speed,
        )
        self.release()
        return True

    def reset(self, server_side: str) -> None:
        """Reposiciona a bola para o lado de quem sacará o próximo ponto.

        Args:
            server_side: Lado sacador. Usa ``"p1"`` para a metade esquerda da
                quadra e qualquer outro valor para a metade direita.
        """
        y = HEIGHT / 2
        if server_side == "p1":
            x = COURT_MARGIN
        else:
            x = WIDTH - COURT_MARGIN

        self.pos.update(x, y)
        self.velocity.update(0, 0)
        self.last_hitter = None
        self.bounce_count = 0
        self.was_served = False
        self.server_side = server_side
        self.last_hit_quality = "normal"
        self.held_by_side = None
        self.rect.center = (round(self.pos.x), round(self.pos.y))
