"""Barras sequenciais de mira e força para a rebatida."""

from __future__ import annotations

import pygame

from src.settings import (
    AIM_MAX_ANGLE,
    AIM_MIN_ANGLE,
    AIM_OSC_SPEED,
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
        owner_side: Lado do dono das barras, ``"bottom"`` ou ``"top"``.
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
            owner_side: Lado do dono das barras, ``"bottom"`` ou ``"top"``.
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

    def draw(self, surface) -> None:
        """Desenha as barras na superfície informada.

        Args:
            surface: Superfície onde as barras devem ser desenhadas.
        """
