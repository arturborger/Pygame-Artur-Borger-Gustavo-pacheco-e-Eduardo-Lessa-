"""Cena principal de gameplay da partida."""

from __future__ import annotations

import pygame
from pygame.math import Vector2

from src.assets_generator import make_court
from src.entities.ai_player import AIPlayer
from src.entities.ball import Ball
from src.entities.player import Player
from src.scenes.base_scene import BaseScene
from src.settings import (
    BALL_BASE_SPEED,
    CONTROLS_P1,
    CONTROLS_P2,
    HEIGHT,
    TOURNAMENT_OPPONENTS,
    WIDTH,
)
from src.systems import physics
from src.systems.collision import player_hits_ball
from src.systems.score_manager import ScoreManager
from src.systems.stats_tracker import StatsTracker


class GameplayScene(BaseScene):
    """Controla uma partida jogável de tênis.

    Args:
        game: Instância principal do jogo.
        mode: Modo de jogo, ``"1p"``, ``"2p"`` ou ``"training"``.
        opponent_id: Identificador do adversário do torneio no modo ``"1p"``.

    Attributes:
        scenery: Identificador visual do cenário atual.
        player1: Jogador da metade inferior da quadra.
        player2: Jogador ou IA da metade superior da quadra.
        ball: Bola ativa da partida.
        score_manager: Placar oficial da partida.
        stats_tracker: Fachada de estatísticas simples para a UI.
        last_hit_time: Tempo da última rebatida válida em milissegundos.
    """

    def __init__(
        self,
        game,
        mode: str = "1p",
        opponent_id: str | None = None,
    ) -> None:
        """Inicializa entidades, placar e assets do gameplay."""
        super().__init__(game)
        self.mode = mode
        self.opponent_config = self._opponent_config(opponent_id)
        self.scenery = self.opponent_config["id"] if mode == "1p" else "beach"
        self.court_surface = self.game.assets.get(
            ("court", self.scenery),
            lambda: make_court(self.scenery),
        )
        self.player1 = Player(self.game.assets, "bottom", CONTROLS_P1, "Voce")
        self.player2 = self._build_second_player()
        self.players = pygame.sprite.Group(self.player1, self.player2)
        self.ball = Ball(self.game.assets, Vector2(WIDTH / 2, HEIGHT / 2))
        self.ball.velocity.update(0, BALL_BASE_SPEED)
        self.ball.was_served = True
        self.score_manager = ScoreManager(self.player1.name, self.player2.name)
        self.stats_tracker = StatsTracker()
        self.last_hit_time = 0
        self._next_scene = None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa eventos de gameplay e repassa travas ao jogador humano.

        Args:
            events: Lista de eventos capturados no quadro atual.
        """
        for event in events:
            self.player1.handle_event(event, self.ball)
            if self.mode == "2p":
                self.player2.handle_event(event, self.ball)

    def update(self, dt: float) -> None:
        """Atualiza jogadores, bola, colisões e física básica.

        Args:
            dt: Tempo decorrido desde o último quadro, em segundos.
        """
        self.player1.update(dt, self.ball)
        self._update_second_player(dt)
        self.ball.update(dt)
        if physics.bounce_off_walls(self.ball):
            self.ball.bounce_count += 1
        self._handle_player_collision(self.player1)
        if self.mode == "2p":
            self._handle_player_collision(self.player2)

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha quadra, jogadores, bola e barras de timing.

        Args:
            surface: Superfície principal onde a cena deve renderizar.
        """
        surface.blit(self.court_surface, (0, 0))
        surface.blit(self.player1.image, self.player1.rect)
        surface.blit(self.player2.image, self.player2.rect)
        surface.blit(self.ball.image, self.ball.rect)
        self.player1.timing_bars.draw(surface)
        self.player2.timing_bars.draw(surface)

    def next_scene(self):
        """Retorna a próxima cena solicitada pelo gameplay.

        Returns:
            Cena seguinte ou ``None`` para manter a partida ativa.
        """
        next_scene = self._next_scene
        self._next_scene = None
        return next_scene

    def _build_second_player(self):
        if self.mode == "1p":
            return AIPlayer(self.game.assets, "top", self.opponent_config)

        return Player(self.game.assets, "top", CONTROLS_P2, "Jogador 2")

    def _update_second_player(self, dt: float) -> None:
        if isinstance(self.player2, AIPlayer):
            hit_result = self.player2.update(dt, self.ball)
            self._register_hit_result(hit_result, self.player2)
        else:
            self.player2.update(dt, self.ball)

    def _handle_player_collision(self, player: Player) -> None:
        if not player_hits_ball(player, self.ball, self.last_hit_time):
            return

        hit_result = player.try_hit(self.ball)
        self._register_hit_result(hit_result, player)

    def _register_hit_result(self, hit_result: str, player: Player) -> None:
        if hit_result not in ("normal", "winner"):
            return

        self.last_hit_time = pygame.time.get_ticks()
        self.ball.was_served = False
        self.ball.last_hit_quality = hit_result
        self.ball.last_hitter = player.side

    def _opponent_config(self, opponent_id: str | None) -> dict:
        if opponent_id is None:
            return TOURNAMENT_OPPONENTS[0]

        for opponent in TOURNAMENT_OPPONENTS:
            if opponent["id"] == opponent_id:
                return opponent

        return TOURNAMENT_OPPONENTS[0]
