"""Funcoes de colisao entre entidades do jogo."""

from __future__ import annotations

import pygame

from src.systems.physics import is_out_of_bounds


def player_hits_ball(
    player: pygame.sprite.Sprite,
    ball: pygame.sprite.Sprite,
    last_hit_time_ms: int,
    cooldown_ms: int = 200,
) -> bool:
    """Verifica se jogador e bola colidiram respeitando um cooldown.

    A colisao usa as mascaras dos sprites para evitar deteccoes imprecisas
    pelo retangulo. O cooldown impede que a mesma sobreposicao gere varias
    rebatidas em quadros consecutivos.

    Args:
        player: Sprite do jogador, com ``rect`` e ``mask``.
        ball: Sprite da bola, com ``rect`` e ``mask``.
        last_hit_time_ms: Tempo em milissegundos da ultima rebatida registrada.
        cooldown_ms: Intervalo minimo entre duas deteccoes validas.

    Returns:
        ``True`` quando ha colisao por mascara e o cooldown ja terminou.
    """
    elapsed_ms = pygame.time.get_ticks() - last_hit_time_ms
    if elapsed_ms < cooldown_ms:
        return False

    return pygame.sprite.collide_mask(player, ball) is not None


def check_ball_out_of_bounds(ball) -> str | None:
    """Delegar a verificacao de saida da bola para o sistema de fisica.

    Args:
        ball: Bola com atributo ``rect`` usado pela funcao de fisica.

    Returns:
        ``"top"``, ``"bottom"`` ou ``None``, conforme ``is_out_of_bounds``.
    """
    return is_out_of_bounds(ball)
