"""Funções de física para movimento e limites da bola."""

from __future__ import annotations

from src.settings import HEIGHT, NET_WIDTH, NET_X, WIDTH


def bounce_off_walls(ball) -> bool:
    """Reflete a bola ao tocar nas bordas superior ou inferior da janela.

    Args:
        ball: Bola com atributos ``rect``, ``pos`` e ``velocity``.

    Returns:
        ``True`` se a bola tocou em uma parede horizontal; caso contrário,
        ``False``.
    """
    if ball.rect.top <= 0:
        ball.rect.top = 0
        ball.pos.y = ball.rect.centery
        ball.velocity.y = abs(ball.velocity.y)
        return True

    if ball.rect.bottom >= HEIGHT:
        ball.rect.bottom = HEIGHT
        ball.pos.y = ball.rect.centery
        ball.velocity.y = -abs(ball.velocity.y)
        return True

    return False


def is_out_of_bounds(ball) -> str | None:
    """Verifica se a bola saiu pelos limites esquerdo ou direito.

    Args:
        ball: Bola com atributo ``rect`` usado para verificar a posição.

    Returns:
        ``"left"`` se saiu pela esquerda, ``"right"`` se saiu pela direita ou
        ``None`` se ainda está dentro dos limites horizontais.
    """
    if ball.rect.right < 0:
        return "left"

    if ball.rect.left > WIDTH:
        return "right"

    return None


def hit_net(ball) -> bool:
    """Verifica se a bola atingiu a faixa da rede.

    Args:
        ball: Bola com atributo ``rect`` usado para verificar a posição.

    Returns:
        ``True`` se a bola cruza a linha vertical da rede dentro da tolerância
        de largura da rede; caso contrário, ``False``.
    """
    return ball.rect.left <= NET_X + NET_WIDTH and ball.rect.right >= NET_X - NET_WIDTH
