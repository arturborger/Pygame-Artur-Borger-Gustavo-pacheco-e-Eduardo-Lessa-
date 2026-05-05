"""Entidade da bola de tênis."""

from __future__ import annotations

import pygame

from src.assets_generator import make_ball
from src.settings import COURT_MARGIN, HEIGHT, WIDTH
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
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt: float) -> None:
        """Atualiza a posição da bola conforme sua velocidade.

        Args:
            dt: Tempo decorrido desde o último quadro, em segundos.
        """
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def reset(self, server_side: str) -> None:
        """Reposiciona a bola para o lado de quem sacará o próximo ponto.

        Args:
            server_side: Lado sacador. Usa ``"p1"`` para a metade inferior da
                quadra e qualquer outro valor para a metade superior.
        """
        x = WIDTH / 2
        if server_side == "p1":
            y = HEIGHT - COURT_MARGIN
        else:
            y = COURT_MARGIN

        self.pos.update(x, y)
        self.velocity.update(0, 0)
        self.last_hitter = None
        self.bounce_count = 0
        self.rect.center = (round(self.pos.x), round(self.pos.y))
