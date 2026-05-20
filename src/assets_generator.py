"""Geradores de assets visuais do jogo de tenis cartoon."""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from src.settings import (
    AI_SPRITE_HEIGHT,
    AI_SPRITE_WIDTH,
    BALL_RADIUS,
    BLACK,
    COURT_HEIGHT,
    COURT_MARGIN_X,
    COURT_MARGIN_Y,
    COURT_WIDTH,
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
NADAL_IDLE_PATH = SPRITES_DIR / "Nadal parado.png"
NADAL_RUN_PATH = SPRITES_DIR / "Nadal correndo.png"
FEDERER_IDLE_PATH = SPRITES_DIR / "Federer parado.png"
FEDERER_RUN_PATH = SPRITES_DIR / "Federer correndo.png"
DJOKOVIC_IDLE_PATH = SPRITES_DIR / "Djokovic parado.png"
DJOKOVIC_RUN_PATH = SPRITES_DIR / "Djokovic correndo.png"


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
        COURT_MARGIN_X,
        COURT_MARGIN_Y,
        COURT_WIDTH,
        COURT_HEIGHT,
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

    head_radius = 19
    head_center = (PLAYER_WIDTH // 2, head_radius + OUTLINE_WIDTH)
    body_rect = pygame.Rect(
        15,
        head_center[1] + head_radius - OUTLINE_WIDTH,
        PLAYER_WIDTH - 30,
        PLAYER_HEIGHT - head_center[1] - head_radius,
    )

    _shadowed_rect(surface, body_rect, color, border_radius=15)
    _shadowed_circle(surface, head_center, head_radius, color)

    return surface


def _remove_near_white_background(image: pygame.Surface, threshold: int = 20) -> pygame.Surface:
    """Remove fundo quase-branco de uma imagem tornando pixels claros transparentes.

    Usado para PNGs de 24 bits sem canal alpha que possuem fundo branco
    (como Federer.png e Djokovic.png). Cria uma nova superficie SRCALPHA e
    zera o alpha de todos os pixels cujos tres canais RGB estejam a menos de
    `threshold` unidades de 255.

    Args:
        image: Superficie pygame original (sem canal alpha proprio).
        threshold: Distancia maxima de cada canal RGB em relacao a 255 para
            considerar um pixel como fundo branco.

    Returns:
        Nova superficie SRCALPHA com o fundo removido.
    """
    result = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    result.blit(image, (0, 0))

    try:
        import numpy as np  # noqa: PLC0415

        rgb = pygame.surfarray.pixels3d(result)
        alpha = pygame.surfarray.pixels_alpha(result)
        white_mask = (
            (rgb[:, :, 0] >= 255 - threshold)
            & (rgb[:, :, 1] >= 255 - threshold)
            & (rgb[:, :, 2] >= 255 - threshold)
        )
        alpha[white_mask] = 0
        del rgb, alpha
    except ImportError:
        result.set_colorkey(WHITE)

    return result


def _load_sprite(path: Path, size: tuple[int, int]) -> pygame.Surface:
    """Carrega um sprite PNG externo e ajusta para o tamanho do jogo.

    PNGs com canal alpha proprio (como Nadal.png) sao convertidos para o
    formato do display via convert_alpha. PNGs sem canal alpha (24 bits,
    como Federer.png e Djokovic.png) passam por remocao de fundo branco
    antes do redimensionamento.
    """
    image = pygame.image.load(str(path))
    has_alpha = image.get_masks()[3] != 0

    if has_alpha:
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            image = image.convert_alpha()
    else:
        image = _remove_near_white_background(image)

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


def make_player_character_sprites(
    sprite_filename: str,
    color: tuple[int, int, int],
) -> tuple[pygame.Surface, pygame.Surface]:
    """Carrega os sprites parado e correndo do personagem selecionado.

    Args:
        sprite_filename: Nome do arquivo ``* parado.png`` em ``assets/sprites/``.
        color: Cor de fallback usada se o arquivo nao puder ser carregado.

    Returns:
        Tupla ``(idle, run)`` com superficies escaladas para
        ``(PLAYER_WIDTH, PLAYER_HEIGHT)``.
    """
    size = (PLAYER_WIDTH, PLAYER_HEIGHT)
    idle_path = SPRITES_DIR / sprite_filename
    run_filename = sprite_filename.replace(" parado", " correndo")
    run_path = SPRITES_DIR / run_filename
    try:
        idle = _load_sprite(idle_path, size)
    except Exception:
        idle = make_player_sprite(color)
    try:
        run = _load_sprite(run_path, size)
    except Exception:
        run = idle
    return idle, run


def make_ai_sprite(opponent_id: int | str) -> pygame.Surface:
    """Carrega o sprite parado de um adversario do torneio."""
    idle, _ = make_ai_sprites(opponent_id)
    return idle


def make_ai_sprites(opponent_id: int | str) -> tuple[pygame.Surface, pygame.Surface]:
    """Carrega os sprites parado e correndo de um adversario do torneio.

    Args:
        opponent_id: Indice ou identificador textual do adversario em
            `TOURNAMENT_OPPONENTS`.

    Returns:
        Tupla ``(idle, run)`` com superficies do adversario.
    """
    if isinstance(opponent_id, int):
        opponent_id = TOURNAMENT_OPPONENTS[opponent_id]["id"]

    size = (AI_SPRITE_WIDTH, AI_SPRITE_HEIGHT)
    if opponent_id == "beach":
        return _load_sprite(NADAL_IDLE_PATH, size), _load_sprite(NADAL_RUN_PATH, size)

    if opponent_id == "forest":
        return _load_sprite(FEDERER_IDLE_PATH, size), _load_sprite(FEDERER_RUN_PATH, size)

    if opponent_id == "stadium":
        return _load_sprite(DJOKOVIC_IDLE_PATH, size), _load_sprite(DJOKOVIC_RUN_PATH, size)

    fallback = make_player_sprite(_get_opponent_color(opponent_id))
    return fallback, fallback


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


def _draw_star(
    surface: pygame.Surface,
    center: tuple[int, int],
    outer_radius: int,
    color: tuple[int, int, int],
) -> None:
    """Desenha uma estrela de oito pontas com contorno preto.

    Args:
        surface: Superficie de destino.
        center: Coordenadas (x, y) do centro da estrela.
        outer_radius: Raio externo da estrela em pixels.
        color: Cor de preenchimento da estrela.
    """
    cx, cy = center
    inner_radius = max(2, outer_radius // 2)
    raw_pts = []
    for i in range(8):
        r = outer_radius if i % 2 == 0 else inner_radius
        angle = math.radians(i * 45 - 90)
        raw_pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    outline_pts = [(int(p[0]), int(p[1])) for p in raw_pts]
    pygame.draw.polygon(surface, BLACK, outline_pts)
    inner_pts = [
        (int(cx + (p[0] - cx) * 0.68), int(cy + (p[1] - cy) * 0.68))
        for p in raw_pts
    ]
    pygame.draw.polygon(surface, color, inner_pts)


def make_victory_animation_frames(
    sprite_filename: str,
    color: tuple[int, int, int],
    frame_count: int = 6,
) -> list[pygame.Surface]:
    """Cria quadros de animacao de vitoria do personagem levantando o trofeu.

    Gera uma sequencia de superficies onde o sprite do personagem aparece
    segurando o trofeu em alturas progressivas, do nivel do peito ate acima
    da cabeca, com estrelas de celebracao que surgem nas fases finais.

    Args:
        sprite_filename: Nome do arquivo PNG em ``assets/sprites/``.
        color: Cor de fallback usada se o sprite nao puder ser carregado.
        frame_count: Numero de quadros na animacao (minimo 2).

    Returns:
        Lista de superficies transparentes representando os quadros da
        animacao de vitoria.
    """
    frame_w, frame_h = 260, 380
    char_w, char_h = 152, 212
    trophy_size = 84

    path = SPRITES_DIR / sprite_filename
    try:
        char_sprite = _load_sprite(path, (char_w, char_h))
    except Exception:
        char_sprite = pygame.transform.scale(make_player_sprite(color), (char_w, char_h))

    trophy_surf = pygame.transform.scale(make_trophy(), (trophy_size, trophy_size))

    char_x = (frame_w - char_w) // 2
    char_y = frame_h - char_h - 14

    # Trofeu sobe do nivel do peito ate acima da cabeca
    trophy_start_cy = char_y + char_h * 2 // 5
    trophy_end_cy = char_y - trophy_size // 2 - 10
    trophy_cx = frame_w // 2

    # Posicoes das estrelas de celebracao ao redor do trofeu levantado
    star_offsets = [(-58, -18), (58, -18), (-38, -54), (38, -54), (0, -68)]
    star_sizes = [7, 6, 8, 6, 7]
    gold = (255, 210, 50)

    frames: list[pygame.Surface] = []
    for i in range(max(frame_count, 2)):
        t = i / (frame_count - 1)
        t_ease = t * t * (3 - 2 * t)  # smooth-step

        trophy_cy = int(trophy_start_cy + (trophy_end_cy - trophy_start_cy) * t_ease)

        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame.blit(char_sprite, (char_x, char_y))
        trophy_rect = trophy_surf.get_rect(center=(trophy_cx, trophy_cy))
        frame.blit(trophy_surf, trophy_rect)

        # Estrelas aparecem progressivamente na segunda metade da animacao
        if t > 0.45:
            for idx, ((dx, dy), size) in enumerate(zip(star_offsets, star_sizes)):
                wave = math.sin(i * 1.3 + idx * 1.1) * 4
                sx = trophy_cx + dx
                sy = trophy_cy + dy + int(wave)
                if 4 < sx < frame_w - 4 and 4 < sy < frame_h - 4:
                    _draw_star(frame, (sx, sy), size, gold)

        frames.append(frame)

    return frames


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
