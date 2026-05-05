"""Funções de física para movimento e limites da bola."""

from __future__ import annotations

from src.settings import HEIGHT, NET_HEIGHT, NET_Y, WIDTH


def bounce_off_walls(ball) -> bool:
    """Reflete a bola ao tocar nas bordas laterais da janela.

    Args:
        ball: Bola com atributos ``rect``, ``pos`` e ``velocity``.

    Returns:
        ``True`` se a bola tocou em uma parede lateral; caso contrário,
        ``False``.
    """
    if ball.rect.left <= 0:
        ball.rect.left = 0
        ball.pos.x = ball.rect.centerx
        ball.velocity.x = abs(ball.velocity.x)
        return True

    if ball.rect.right >= WIDTH:
        ball.rect.right = WIDTH
        ball.pos.x = ball.rect.centerx
        ball.velocity.x = -abs(ball.velocity.x)
        return True

    return False


def is_out_of_bounds(ball) -> str | None:
    """Verifica se a bola saiu pelos limites superior ou inferior.

    Args:
        ball: Bola com atributo ``rect`` usado para verificar a posição.

    Returns:
        ``"top"`` se saiu pelo topo, ``"bottom"`` se saiu por baixo ou
        ``None`` se ainda está dentro dos limites verticais.
    """
    if ball.rect.bottom < 0:
        return "top"

    if ball.rect.top > HEIGHT:
        return "bottom"

    return None


def hit_net(ball) -> bool:
    """Verifica se a bola atingiu a faixa da rede.

    Args:
        ball: Bola com atributo ``rect`` usado para verificar a posição.

    Returns:
        ``True`` se a bola cruza a linha da rede dentro da tolerância de altura
        da rede; caso contrário, ``False``.
    """
    return ball.rect.top <= NET_Y + NET_HEIGHT and ball.rect.bottom >= NET_Y - NET_HEIGHT
