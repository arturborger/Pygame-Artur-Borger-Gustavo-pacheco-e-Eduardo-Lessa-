"""Barras sequenciais de mira e força para a rebatida."""

from __future__ import annotations

import pygame

from src.settings import (
    AIM_MAX_ANGLE,
    AIM_MIN_ANGLE,
    AIM_OSC_SPEED,
    BAR_BORDER_RADIUS,
    BAR_CURSOR_WIDTH,
    BAR_HEIGHT,
    BAR_OUTLINE_WIDTH,
    BAR_SPACING,
    BAR_WIDTH,
    COURT_MARGIN,
    GRAY_INACTIVE,
    GRAY_LIGHT,
    GREEN_LOCKED,
    GREEN_SWEET,
    LINE_OUTLINE,
    ORANGE,
    POWER_MAX,
    POWER_MIN,
    POWER_OSC_SPEED,
    SHOW_FROZEN_TIME,
    SWEET_SPOT_HIGH,
    SWEET_SPOT_LOW,
)


class TimingBars:
    """Controla o estado das barras de timing de um jogador.

    Args:
        owner_side: Lado do dono das barras, ``"left"`` ou ``"right"``.
        lock_key: Código da tecla usada para travar as barras.

    Attributes:
        state: Estado atual da mecânica sequencial.
        aim_value: Valor atual da barra de ângulo, em graus.
        aim_direction: Direção atual da oscilação do ângulo.
        power_value: Valor atual da barra de força.
        power_direction: Direção atual da oscilação da força.
        locked_angle: Ângulo travado pelo jogador.
        locked_power: Força travada pelo jogador.
        frozen_until: Instante em milissegundos até o qual as barras ficam congeladas.
    """

    STATE_IDLE = "IDLE"
    STATE_AIMING = "AIMING"
    STATE_POWERING = "POWERING"
    STATE_LOCKED = "LOCKED"

    def __init__(self, owner_side: str, lock_key: int) -> None:
        """Inicializa as barras em repouso.

        Args:
            owner_side: Lado do dono das barras, ``"left"`` ou ``"right"``.
            lock_key: Código Pygame da tecla usada para travar a barra atual.
        """
        self.owner_side = owner_side
        self.lock_key = lock_key
        self.state = self.STATE_IDLE
        self.aim_value = 0.0
        self.aim_direction = 1
        self.power_value = POWER_MIN
        self.power_direction = 1
        self.locked_angle: float | None = None
        self.locked_power: float | None = None
        self.frozen_until = 0

    def activate(self) -> None:
        """Ativa a barra de ângulo e inicia a oscilação."""
        self.state = self.STATE_AIMING
        self.aim_value = 0.0
        self.aim_direction = 1
        self.power_value = POWER_MIN
        self.power_direction = 1
        self.locked_angle = None
        self.locked_power = None
        self.frozen_until = 0

    def update(self, dt: float) -> None:
        """Atualiza a oscilação da barra ativa.

        Args:
            dt: Tempo decorrido desde o último quadro, em segundos.
        """
        if self.state == self.STATE_AIMING:
            self.aim_value += self.aim_direction * AIM_OSC_SPEED * dt

            if self.aim_value >= AIM_MAX_ANGLE:
                self.aim_value = AIM_MAX_ANGLE
                self.aim_direction = -1
            elif self.aim_value <= AIM_MIN_ANGLE:
                self.aim_value = AIM_MIN_ANGLE
                self.aim_direction = 1

        if self.state == self.STATE_POWERING:
            self.power_value += self.power_direction * POWER_OSC_SPEED * dt

            if self.power_value >= POWER_MAX:
                self.power_value = POWER_MAX
                self.power_direction = -1
            elif self.power_value <= POWER_MIN:
                self.power_value = POWER_MIN
                self.power_direction = 1

    def reset(self) -> None:
        """Retorna as barras ao estado inicial inativo."""
        self.state = self.STATE_IDLE
        self.aim_value = 0.0
        self.aim_direction = 1
        self.power_value = POWER_MIN
        self.power_direction = 1
        self.locked_angle = None
        self.locked_power = None
        self.frozen_until = 0

    def is_locked(self) -> bool:
        """Indica se as barras já foram travadas.

        Returns:
            ``True`` quando as barras estão no estado ``LOCKED``.
        """
        return self.state == self.STATE_LOCKED

    def is_active(self) -> bool:
        """Indica se alguma etapa das barras está ativa.

        Returns:
            ``True`` quando o estado atual não é ``IDLE``.
        """
        return self.state != self.STATE_IDLE

    def handle_lock_press(self) -> bool:
        """Processa a tecla de travamento.

        Returns:
            ``True`` quando o pressionamento muda a etapa atual; caso contrário,
            ``False``.
        """
        if self.state == self.STATE_AIMING:
            self.locked_angle = self.aim_value
            self.state = self.STATE_POWERING
            self.power_value = POWER_MIN
            self.power_direction = 1
            return True

        if self.state == self.STATE_POWERING:
            self.locked_power = self.power_value
            self.state = self.STATE_LOCKED
            self.frozen_until = pygame.time.get_ticks() + int(SHOW_FROZEN_TIME * 1000)
            return True

        return False

    def get_locked_values(self) -> tuple[float, float] | None:
        """Retorna os valores travados de ângulo e força.

        Returns:
            Tupla ``(locked_angle, locked_power)`` quando as barras estão
            travadas, ou ``None`` antes disso.
        """
        if (
            self.state != self.STATE_LOCKED
            or self.locked_angle is None
            or self.locked_power is None
        ):
            return None

        return self.locked_angle, self.locked_power

    def is_sweet_spot(self) -> bool:
        """Indica se a força travada está na zona ideal.

        Returns:
            ``True`` quando a força travada está entre os limites do sweet spot.
        """
        if self.locked_power is None:
            return False

        return SWEET_SPOT_LOW <= self.locked_power <= SWEET_SPOT_HIGH

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha as barras na superfície informada.

        Args:
            surface: Superfície onde as barras devem ser desenhadas.
        """
        if self.state == self.STATE_IDLE:
            return

        angle_rect, power_rect = self._bar_rects(surface)

        self._draw_bar_background(surface, angle_rect)
        self._draw_angle_cursor(surface, angle_rect)

        self._draw_bar_background(surface, power_rect)
        self._draw_sweet_spot(surface, power_rect)
        self._draw_power_cursor(surface, power_rect)

    def _bar_rects(self, surface: pygame.Surface) -> tuple[pygame.Rect, pygame.Rect]:
        total_height = BAR_HEIGHT * 2 + BAR_SPACING
        y = surface.get_height() - COURT_MARGIN // 2 - total_height

        if self.owner_side == "right":
            x = surface.get_width() - COURT_MARGIN // 2 - BAR_WIDTH
        elif self.owner_side == "left":
            x = COURT_MARGIN // 2
        else:
            x = (surface.get_width() - BAR_WIDTH) // 2

        angle_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
        power_rect = angle_rect.move(0, BAR_HEIGHT + BAR_SPACING)
        return angle_rect, power_rect

    def _draw_bar_background(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        inner_rect = rect.inflate(-BAR_OUTLINE_WIDTH * 2, -BAR_OUTLINE_WIDTH * 2)
        inner_radius = max(0, BAR_BORDER_RADIUS - BAR_OUTLINE_WIDTH)

        pygame.draw.rect(
            surface,
            LINE_OUTLINE,
            rect,
            border_radius=BAR_BORDER_RADIUS,
        )
        pygame.draw.rect(
            surface,
            GRAY_LIGHT,
            inner_rect,
            border_radius=inner_radius,
        )

    def _draw_angle_cursor(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        if self.state in (self.STATE_POWERING, self.STATE_LOCKED):
            self._draw_locked_angle_marker(surface, rect)

        color = ORANGE if self.state == self.STATE_AIMING else GRAY_INACTIVE
        self._draw_cursor(
            surface,
            rect,
            self.aim_value,
            AIM_MIN_ANGLE,
            AIM_MAX_ANGLE,
            color,
        )

    def _draw_locked_angle_marker(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        if self.locked_angle is None:
            return

        marker_width = BAR_CURSOR_WIDTH + BAR_OUTLINE_WIDTH * 2
        self._draw_cursor(
            surface,
            rect,
            self.locked_angle,
            AIM_MIN_ANGLE,
            AIM_MAX_ANGLE,
            GREEN_LOCKED,
            marker_width,
        )

    def _draw_sweet_spot(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        track_rect = rect.inflate(-BAR_OUTLINE_WIDTH * 2, -BAR_OUTLINE_WIDTH * 2)
        start_ratio = self._normalized_ratio(SWEET_SPOT_LOW, POWER_MIN, POWER_MAX)
        end_ratio = self._normalized_ratio(SWEET_SPOT_HIGH, POWER_MIN, POWER_MAX)
        sweet_left = track_rect.left + round(start_ratio * track_rect.width)
        sweet_right = track_rect.left + round(end_ratio * track_rect.width)
        sweet_rect = pygame.Rect(
            sweet_left,
            track_rect.top,
            sweet_right - sweet_left,
            track_rect.height,
        )

        pygame.draw.rect(
            surface,
            GREEN_SWEET,
            sweet_rect,
            border_radius=max(0, BAR_BORDER_RADIUS - BAR_OUTLINE_WIDTH),
        )

    def _draw_power_cursor(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self.state == self.STATE_LOCKED:
            value = self.locked_power
        else:
            value = self.power_value

        if value is None:
            value = self.power_value

        if self.state == self.STATE_POWERING:
            color = ORANGE
        elif self.state == self.STATE_LOCKED:
            color = GREEN_LOCKED
        else:
            color = GRAY_INACTIVE

        self._draw_cursor(surface, rect, value, POWER_MIN, POWER_MAX, color)

    def _draw_cursor(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        value: float,
        minimum: float,
        maximum: float,
        color: tuple[int, int, int],
        width: int = BAR_CURSOR_WIDTH,
    ) -> None:
        ratio = self._normalized_ratio(value, minimum, maximum)
        min_x = rect.left + width // 2
        max_x = rect.right - width // 2
        cursor_x = min_x + round(ratio * (max_x - min_x))
        cursor_height = BAR_HEIGHT + BAR_OUTLINE_WIDTH * 2
        cursor_rect = pygame.Rect(0, 0, width, cursor_height)
        cursor_rect.center = (cursor_x, rect.centery)

        pygame.draw.rect(
            surface,
            LINE_OUTLINE,
            cursor_rect,
            border_radius=BAR_BORDER_RADIUS,
        )
        pygame.draw.rect(
            surface,
            color,
            cursor_rect.inflate(-BAR_OUTLINE_WIDTH * 2, -BAR_OUTLINE_WIDTH * 2),
            border_radius=max(0, BAR_BORDER_RADIUS - BAR_OUTLINE_WIDTH),
        )

    def _normalized_ratio(self, value: float, minimum: float, maximum: float) -> float:
        ratio = (value - minimum) / (maximum - minimum)
        return max(0.0, min(1.0, ratio))
