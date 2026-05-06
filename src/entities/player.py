"""Entidade do jogador humano."""

from __future__ import annotations

import pygame
from pygame.math import Vector2

from src.assets_generator import make_player_sprite
from src.settings import (
    BLUE,
    COURT_MARGIN,
    HEIGHT,
    HIT_RADIUS,
    NET_WIDTH,
    NET_X,
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
        side: Lado da quadra ocupado pelo jogador, ``"left"`` ou ``"right"``.
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

        color = BLUE if side == "left" else RED
        self.image = asset_cache.get(
            ("player_sprite", side, color),
            lambda: make_player_sprite(color),
        )
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        start_x = (
            COURT_MARGIN + PLAYER_WIDTH // 2
            if side == "left"
            else WIDTH - COURT_MARGIN - PLAYER_WIDTH // 2
        )
        self.pos = Vector2(start_x, HEIGHT / 2)
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

    def handle_event(self, event: pygame.event.Event, ball) -> str:
        """Processa eventos pontuais do jogador.

        Args:
            event: Evento recebido da fila do Pygame.
            ball: Bola atual da partida, mantida na assinatura para integracao
                com a cena de gameplay.

        Returns:
            Resultado da rebatida quando o segundo travamento solta a bola, ou
            ``"no_hit"`` nos demais eventos.
        """
        if event.type != pygame.KEYDOWN:
            return "no_hit"

        if event.key == self.controls.get("lock", pygame.K_SPACE):
            changed_state = self.timing_bars.handle_lock_press()
            if changed_state and self.timing_bars.is_locked():
                return self.try_hit(ball)

        return "no_hit"

    def capture_ball(self, ball) -> bool:
        """Para a bola no jogador e habilita as barras sequenciais.

        Args:
            ball: Bola que acabou de colidir com o jogador.

        Returns:
            ``True`` quando a bola foi presa e as barras foram ativadas.
        """
        if ball.is_held() or not self._ball_is_approaching(ball):
            return False

        ball.capture_by_player(self)
        self.timing_bars.activate()
        return True

    def can_hit(self, ball) -> bool:
        """Verifica se a bola esta dentro do raio de rebatida.

        Args:
            ball: Bola com atributo `rect.center`.

        Returns:
            ``True`` quando a distancia ate a bola e menor ou igual a
            `HIT_RADIUS`.
        """
        player_center = Vector2(self.rect.center)
        ball_center = Vector2(ball.rect.center)
        return player_center.distance_to(ball_center) <= HIT_RADIUS

    def try_hit(self, ball) -> str:
        """Tenta aplicar uma rebatida na bola.

        Args:
            ball: Bola que pode receber a rebatida.

        Returns:
            `"winner"` para rebatida no sweet spot, `"normal"` para rebatida
            comum, `"miss"` quando a bola passou apos as barras travadas ou
            `"no_hit"` quando nada deve acontecer neste quadro.
        """
        if not self.timing_bars.is_locked():
            return "no_hit"

        locked_values = self.timing_bars.get_locked_values()
        if locked_values is None:
            return "no_hit"

        held_by_side = getattr(ball, "held_by_side", None)
        if held_by_side is not None and held_by_side != self.side:
            return "no_hit"

        if held_by_side == self.side or self.can_hit(ball):
            angle, power = locked_values
            is_sweet = self.timing_bars.is_sweet_spot()
            ball.apply_shot(angle, power, self.side, is_sweet)
            ball.last_hitter = self.side
            ball.bounce_count = 0
            self.timing_bars.reset()
            return "winner" if is_sweet else "normal"

        if self._ball_has_passed(ball):
            self.timing_bars.reset()
            return "miss"

        return "no_hit"

    def update(self, dt: float, ball=None) -> None:
        """Atualiza movimento, barras e bola presa ao jogador.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
            ball: Bola usada para acompanhar o jogador durante a mira.
        """
        keys = pygame.key.get_pressed()
        self.handle_input(keys, dt)
        if ball is not None:
            self._follow_held_ball(ball)
        self.timing_bars.update(dt)

    def _follow_held_ball(self, ball) -> None:
        if getattr(ball, "held_by_side", None) == self.side:
            ball.follow_captured_player(self)

    def _clamp_to_own_court(self) -> None:
        half_width = PLAYER_WIDTH / 2
        half_height = PLAYER_HEIGHT / 2
        min_y = COURT_MARGIN + half_height
        max_y = HEIGHT - COURT_MARGIN - half_height

        if self.side == "left":
            min_x = COURT_MARGIN + half_width
            max_x = NET_X - NET_WIDTH / 2 - half_width
        else:
            min_x = NET_X + NET_WIDTH / 2 + half_width
            max_x = WIDTH - COURT_MARGIN - half_width

        self.pos.x = max(min_x, min(max_x, self.pos.x))
        self.pos.y = max(min_y, min(max_y, self.pos.y))

    def _ball_is_approaching(self, ball) -> bool:
        if self.side == "left":
            return ball.velocity.x < 0

        return ball.velocity.x > 0

    def _ball_has_passed(self, ball) -> bool:
        if self.side == "left":
            return ball.rect.centerx < self.rect.centerx - HIT_RADIUS

        return ball.rect.centerx > self.rect.centerx + HIT_RADIUS
