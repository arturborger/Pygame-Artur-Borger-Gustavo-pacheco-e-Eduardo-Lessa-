"""Geradores de assets visuais do jogo de tenis cartoon."""

from __future__ import annotations

from pathlib import Path

import pygame

from src.settings import (
    BALL_RADIUS,
    BLACK,
    COURT_MARGIN,
    HEIGHT,
    NET_WIDTH,
    NET_X,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    SCENERY_COLORS,
    TOURNAMENT_OPPONENTS,
    WHITE,
    WIDTH,
    YELLOW,
)

OUTLINE_WIDTH = 3
SHADOW_OFFSET = (3, 3)
SHADOW_COLOR = (0, 0, 0, 60)
COURT_LINE_WIDTH = 4
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPRITES_DIR = PROJECT_ROOT / "assets" / "sprites"
NADAL_SPRITE_PATH = SPRITES_DIR / "Nadal.png"


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
    center_y = court_rect.centery
    left_service_x = (left + NET_X) // 2
    right_service_x = (NET_X + right) // 2

    _shadowed_line(surface, line_color, (left, top), (right, top), COURT_LINE_WIDTH)
    _shadowed_line(surface, line_color, (left, bottom), (right, bottom), COURT_LINE_WIDTH)
    _shadowed_line(surface, line_color, (left, top), (left, bottom), COURT_LINE_WIDTH)
    _shadowed_line(surface, line_color, (right, top), (right, bottom), COURT_LINE_WIDTH)
    _shadowed_line(
        surface,
        line_color,
        (left_service_x, top),
        (left_service_x, bottom),
        COURT_LINE_WIDTH,
    )
    _shadowed_line(
        surface,
        line_color,
        (right_service_x, top),
        (right_service_x, bottom),
        COURT_LINE_WIDTH,
    )
    _shadowed_line(
        surface,
        line_color,
        (left_service_x, center_y),
        (right_service_x, center_y),
        COURT_LINE_WIDTH,
    )

    net_rect = pygame.Rect(NET_X - NET_WIDTH // 2, top, NET_WIDTH, bottom - top)
    _shadowed_rect(surface, net_rect, line_color, border_radius=NET_WIDTH // 2)

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


def _load_sprite(path: Path, size: tuple[int, int]) -> pygame.Surface:
    """Carrega um sprite PNG externo e ajusta para o tamanho do jogo."""
    image = pygame.image.load(str(path))
    if pygame.display.get_init() and pygame.display.get_surface() is not None:
        image = image.convert_alpha()

    return pygame.transform.smoothscale(image, size)


def _blit_rotated_with_pivot(
    target: pygame.Surface,
    image: pygame.Surface,
    pivot_pos: tuple[int, int],
    pivot_offset: tuple[int, int],
    angle: float,
) -> None:
    """Desenha uma imagem rotacionada mantendo um ponto de pivo fixo."""
    rotated_image = pygame.transform.rotate(image, angle)
    image_center = pygame.math.Vector2(image.get_rect().center)
    pivot_vector = pygame.math.Vector2(pivot_offset)
    rotated_offset = (pivot_vector - image_center).rotate(-angle)
    rotated_center = pygame.math.Vector2(pivot_pos) - rotated_offset
    rotated_rect = rotated_image.get_rect(center=rotated_center)
    target.blit(rotated_image, rotated_rect)


def make_swing_animation_frames(color: tuple[int, int, int]) -> list[pygame.Surface]:
    """Cria quadros de animacao de rebatida para o jogador.

    Args:
        color: Cor chapada usada no corpo do jogador e no braco.

    Returns:
        Lista com 4 superficies transparentes, todas do mesmo tamanho,
        representando uma rebatida com a raquete em angulos diferentes.
    """
    frame_size = (PLAYER_WIDTH + 80, PLAYER_HEIGHT + 52)
    player_offset = ((frame_size[0] - PLAYER_WIDTH) // 2, 26)
    shoulder = (
        player_offset[0] + PLAYER_WIDTH // 2 + 12,
        player_offset[1] + PLAYER_HEIGHT // 2 + 2,
    )
    angles = (-55, -20, 20, 55)

    arm = pygame.Surface((58, 14), pygame.SRCALPHA)
    pygame.draw.rect(arm, BLACK, pygame.Rect(0, 0, 58, 14), border_radius=6)
    pygame.draw.rect(arm, color, pygame.Rect(3, 3, 34, 8), border_radius=4)
    pygame.draw.rect(arm, WHITE, pygame.Rect(33, 4, 18, 6), border_radius=3)
    pygame.draw.rect(arm, BLACK, pygame.Rect(48, 1, 9, 12), border_radius=5)
    pygame.draw.rect(arm, WHITE, pygame.Rect(50, 3, 5, 8), border_radius=4)

    player_sprite = make_player_sprite(color)
    frames: list[pygame.Surface] = []
    for angle in angles:
        frame = pygame.Surface(frame_size, pygame.SRCALPHA)
        frame.blit(player_sprite, player_offset)
        _blit_rotated_with_pivot(frame, arm, shoulder, (0, arm.get_height() // 2), angle)
        pygame.draw.circle(frame, BLACK, shoulder, 7)
        pygame.draw.circle(frame, color, shoulder, 4)
        frames.append(frame)

    return frames


def make_ai_sprite(opponent_id: int | str) -> pygame.Surface:
    """Cria ou carrega o sprite de um adversario do torneio.

    Args:
        opponent_id: Indice ou identificador textual do adversario em
            `TOURNAMENT_OPPONENTS`.

    Returns:
        Superficie transparente com o sprite do adversario.
    """
    if opponent_id == "beach" or (
        isinstance(opponent_id, int)
        and TOURNAMENT_OPPONENTS[opponent_id]["id"] == "beach"
    ):
        return _load_sprite(NADAL_SPRITE_PATH, (PLAYER_WIDTH, PLAYER_HEIGHT))

    return make_player_sprite(_get_opponent_color(opponent_id))


def make_ball() -> pygame.Surface:
    """Cria a imagem cartoon da bola de tenis.

    Returns:
        Superficie transparente com uma bola amarela, contorno preto e linhas
        curvas brancas de bola de tenis.
    """
    diameter = BALL_RADIUS * 2 + OUTLINE_WIDTH * 2
    surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    center = (diameter // 2, diameter // 2)
    radius = BALL_RADIUS + OUTLINE_WIDTH

    pygame.draw.circle(surface, BLACK, center, radius)
    pygame.draw.circle(surface, YELLOW, center, BALL_RADIUS)

    arc_width = 2
    left_arc = pygame.Rect(1, 3, diameter - 6, diameter - 6)
    right_arc = pygame.Rect(5, 3, diameter - 6, diameter - 6)
    pygame.draw.arc(surface, WHITE, left_arc, -1.35, 1.35, arc_width)
    pygame.draw.arc(surface, WHITE, right_arc, 1.8, 4.48, arc_width)

    return surface


def make_trophy() -> pygame.Surface:
    """Cria a imagem cartoon de um trofeu dourado.

    Returns:
        Superficie transparente com um trofeu dourado em estilo cartoon e base
        preta.
    """
    surface = pygame.Surface((96, 96), pygame.SRCALPHA)
    gold = (255, 200, 60)
    gold_light = (255, 230, 120)
    gold_shadow = (215, 145, 35)

    left_handle = pygame.Rect(12, 18, 32, 34)
    right_handle = pygame.Rect(52, 18, 32, 34)
    pygame.draw.arc(surface, BLACK, left_handle, 1.55, 4.75, OUTLINE_WIDTH + 2)
    pygame.draw.arc(surface, BLACK, right_handle, -1.6, 1.6, OUTLINE_WIDTH + 2)
    pygame.draw.arc(surface, gold, left_handle, 1.55, 4.75, OUTLINE_WIDTH)
    pygame.draw.arc(surface, gold, right_handle, -1.6, 1.6, OUTLINE_WIDTH)

    cup_points = [(28, 14), (68, 14), (64, 54), (56, 66), (40, 66), (32, 54)]
    pygame.draw.polygon(surface, BLACK, cup_points)
    inner_cup = [(32, 18), (64, 18), (60, 52), (53, 61), (43, 61), (36, 52)]
    pygame.draw.polygon(surface, gold, inner_cup)
    pygame.draw.rect(surface, gold_light, pygame.Rect(36, 22, 8, 28), border_radius=4)
    pygame.draw.arc(surface, gold_shadow, pygame.Rect(36, 39, 24, 22), 0.0, 3.14, 3)

    pygame.draw.rect(surface, BLACK, pygame.Rect(42, 62, 12, 14), border_radius=2)
    pygame.draw.rect(surface, gold, pygame.Rect(45, 62, 6, 14), border_radius=2)
    pygame.draw.rect(surface, BLACK, pygame.Rect(30, 74, 36, 10), border_radius=3)
    pygame.draw.rect(surface, gold_shadow, pygame.Rect(34, 74, 28, 6), border_radius=2)
    pygame.draw.rect(surface, BLACK, pygame.Rect(20, 82, 56, 10), border_radius=3)

    return surface


def make_button(
    text: str,
    color: tuple[int, int, int],
    width: int,
    height: int,
) -> pygame.Surface:
    """Cria a imagem cartoon de um botao com texto centralizado.

    Args:
        text: Texto exibido no centro do botao.
        color: Cor de preenchimento do botao.
        width: Largura da superficie do botao, em pixels.
        height: Altura da superficie do botao, em pixels.

    Returns:
        Superficie transparente com botao arredondado, contorno preto grosso e
        texto branco em negrito.
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    border_width = OUTLINE_WIDTH + 1
    border_radius = min(14, height // 3)
    button_rect = pygame.Rect(0, 0, width, height)
    inner_rect = button_rect.inflate(-border_width * 2, -border_width * 2)

    pygame.draw.rect(surface, BLACK, button_rect, border_radius=border_radius)
    pygame.draw.rect(
        surface,
        color,
        inner_rect,
        border_radius=max(0, border_radius - border_width),
    )

    if not pygame.font.get_init():
        pygame.font.init()

    font_size = max(16, min(36, height // 2))
    font = pygame.font.Font(None, font_size)
    font.set_bold(True)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    surface.blit(text_surface, text_rect)

    return surface
