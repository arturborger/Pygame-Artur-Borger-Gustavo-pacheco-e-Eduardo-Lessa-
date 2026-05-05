"""Geradores de assets visuais do jogo de tenis cartoon."""

from __future__ import annotations

import pygame

from src.settings import (
    BLACK,
    COURT_MARGIN,
    HEIGHT,
    NET_HEIGHT,
    NET_Y,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    SCENERY_COLORS,
    TOURNAMENT_OPPONENTS,
    WIDTH,
)

OUTLINE_WIDTH = 3
SHADOW_OFFSET = (3, 3)
SHADOW_COLOR = (0, 0, 0, 60)
COURT_LINE_WIDTH = 4


def _shadowed_rect(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: tuple[int, int, int],
    border_radius: int = 0,
) -> None:
    """Desenha um retangulo preenchido com sombra e contorno."""
    shadow_rect = rect.move(SHADOW_OFFSET)
    pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=border_radius)
    pygame.draw.rect(surface, BLACK, rect, border_radius=border_radius)
    inner_rect = rect.inflate(-OUTLINE_WIDTH * 2, -OUTLINE_WIDTH * 2)
    pygame.draw.rect(surface, color, inner_rect, border_radius=max(0, border_radius - 2))


def _shadowed_circle(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    """Desenha um circulo preenchido com sombra e contorno."""
    shadow_center = (center[0] + SHADOW_OFFSET[0], center[1] + SHADOW_OFFSET[1])
    pygame.draw.circle(surface, SHADOW_COLOR, shadow_center, radius)
    pygame.draw.circle(surface, BLACK, center, radius)
    pygame.draw.circle(surface, color, center, radius - OUTLINE_WIDTH)


def _shadowed_line(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    start_pos: tuple[int, int],
    end_pos: tuple[int, int],
    width: int,
) -> None:
    """Desenha uma linha com sombra e contorno preto."""
    shadow_start = (start_pos[0] + SHADOW_OFFSET[0], start_pos[1] + SHADOW_OFFSET[1])
    shadow_end = (end_pos[0] + SHADOW_OFFSET[0], end_pos[1] + SHADOW_OFFSET[1])
    outline_width = width + OUTLINE_WIDTH * 2
    pygame.draw.line(surface, SHADOW_COLOR, shadow_start, shadow_end, outline_width)
    pygame.draw.line(surface, BLACK, start_pos, end_pos, outline_width)
    pygame.draw.line(surface, color, start_pos, end_pos, width)


def _get_opponent_color(opponent_id: int | str) -> tuple[int, int, int]:
    """Retorna a cor de um adversario por indice ou identificador textual."""
    if isinstance(opponent_id, int):
        return TOURNAMENT_OPPONENTS[opponent_id]["color"]

    for opponent in TOURNAMENT_OPPONENTS:
        if opponent["id"] == opponent_id:
            return opponent["color"]

    raise ValueError(f"Adversario desconhecido: {opponent_id!r}")


def make_court(scenery_id: str) -> pygame.Surface:
    """Cria uma superficie com a quadra de tenis do cenario escolhido.

    Args:
        scenery_id: Identificador do cenario em `SCENERY_COLORS`.

    Returns:
        Superficie com canal alpha, fundo, quadra, linhas simples e rede.

    Raises:
        KeyError: Se `scenery_id` nao existir em `SCENERY_COLORS`.
    """
    palette = SCENERY_COLORS[scenery_id]
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surface.fill(palette["bg"])

    court_rect = pygame.Rect(
        COURT_MARGIN,
        COURT_MARGIN,
        WIDTH - COURT_MARGIN * 2,
        HEIGHT - COURT_MARGIN * 2,
    )
    _shadowed_rect(surface, court_rect, palette["court"])

    line_color = palette["lines"]
    left = court_rect.left + OUTLINE_WIDTH
    right = court_rect.right - OUTLINE_WIDTH
    top = court_rect.top + OUTLINE_WIDTH
    bottom = court_rect.bottom - OUTLINE_WIDTH
    center_x = court_rect.centerx
    top_service_y = (top + NET_Y) // 2
    bottom_service_y = (NET_Y + bottom) // 2

    _shadowed_line(surface, line_color, (left, top), (right, top), COURT_LINE_WIDTH)
    _shadowed_line(surface, line_color, (left, bottom), (right, bottom), COURT_LINE_WIDTH)
    _shadowed_line(surface, line_color, (left, top), (left, bottom), COURT_LINE_WIDTH)
    _shadowed_line(surface, line_color, (right, top), (right, bottom), COURT_LINE_WIDTH)
    _shadowed_line(
        surface,
        line_color,
        (left, top_service_y),
        (right, top_service_y),
        COURT_LINE_WIDTH,
    )
    _shadowed_line(
        surface,
        line_color,
        (left, bottom_service_y),
        (right, bottom_service_y),
        COURT_LINE_WIDTH,
    )
    _shadowed_line(
        surface,
        line_color,
        (center_x, top_service_y),
        (center_x, bottom_service_y),
        COURT_LINE_WIDTH,
    )

    net_rect = pygame.Rect(left, NET_Y - NET_HEIGHT // 2, right - left, NET_HEIGHT)
    _shadowed_rect(surface, net_rect, line_color, border_radius=NET_HEIGHT // 2)

    return surface


def make_player_sprite(color: tuple[int, int, int]) -> pygame.Surface:
    """Cria o sprite cartoon de um jogador.

    Args:
        color: Cor chapada usada na cabeca e no corpo do jogador.

    Returns:
        Superficie transparente com um sprite de jogador em estilo cartoon.
    """
    surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

    head_radius = 15
    head_center = (PLAYER_WIDTH // 2, head_radius + OUTLINE_WIDTH)
    body_rect = pygame.Rect(
        12,
        head_center[1] + head_radius - OUTLINE_WIDTH,
        PLAYER_WIDTH - 24,
        PLAYER_HEIGHT - head_center[1] - head_radius,
    )

    _shadowed_rect(surface, body_rect, color, border_radius=12)
    _shadowed_circle(surface, head_center, head_radius, color)

    return surface


def make_ai_sprite(opponent_id: int | str) -> pygame.Surface:
    """Cria o sprite cartoon de um adversario do torneio.

    Args:
        opponent_id: Indice ou identificador textual do adversario em
            `TOURNAMENT_OPPONENTS`.

    Returns:
        Superficie transparente com o sprite do adversario.
    """
    return make_player_sprite(_get_opponent_color(opponent_id))
