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
        self.score_manager = ScoreManager(self.player1.name, self.player2.name)
        self.stats_tracker = StatsTracker()
        self.ball = Ball(self.game.assets, Vector2(WIDTH / 2, HEIGHT / 2))
        self._serve_ball()
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
        if self._next_scene is not None:
            return

        self.player1.update(dt, self.ball)
        self._update_second_player(dt)
        self.ball.update(dt)
        if physics.bounce_off_walls(self.ball):
            self.ball.bounce_count += 1

        out_side = physics.is_out_of_bounds(self.ball)
        if out_side is not None:
            self._award_point(out_side)
            return

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
        self.ball.last_hit_quality = hit_result
        self.ball.last_hitter = player.side
        if self._score_side_for_player_side(player.side) != self.ball.server_side:
            self.ball.was_served = False

    def _award_point(self, out_side: str) -> None:
        winner_side = "p1" if out_side == "top" else "p2"
        point_type = self._point_type_for(winner_side)
        self.score_manager.add_point(winner_side, point_type)
        self._register_point_stat(winner_side, point_type)
        self._play_sound("score")

        if self.score_manager.is_match_over():
            self._freeze_match()
            self._next_scene = self._build_stats_scene()
            return

        self._reset_point()

    def _point_type_for(self, winner_side: str) -> str:
        winner_player_side = self._player_side_for_score_side(winner_side)
        direct_point = (
            self.ball.last_hitter == winner_player_side
            and self.ball.bounce_count == 0
        )

        if not direct_point:
            return "normal"

        if self.ball.was_served and self.ball.server_side == winner_side:
            return "ace"

        if getattr(self.ball, "last_hit_quality", "normal") == "winner":
            return "winner"

        return "normal"

    def _register_point_stat(self, winner_side: str, point_type: str) -> None:
        if point_type == "ace":
            self.stats_tracker.register_ace(winner_side)
        elif point_type == "winner":
            self.stats_tracker.register_winner(winner_side)

    def _reset_point(self) -> None:
        self.ball.reset(self.score_manager.server())
        self._serve_ball()
        self.player1.timing_bars.reset()
        self.player2.timing_bars.reset()
        self.last_hit_time = pygame.time.get_ticks()

    def _serve_ball(self) -> None:
        server_side = self.score_manager.server()
        player_side = self._player_side_for_score_side(server_side)
        direction_y = -1 if server_side == "p1" else 1
        self.ball.velocity.update(0, BALL_BASE_SPEED * direction_y)
        self.ball.server_side = server_side
        self.ball.was_served = True
        self.ball.last_hitter = player_side
        self.ball.last_hit_quality = "normal"
        self.ball.bounce_count = 0

    def _freeze_match(self) -> None:
        self.ball.velocity.update(0, 0)
        self.player1.timing_bars.reset()
        self.player2.timing_bars.reset()

    def _build_stats_scene(self):
        try:
            module = __import__("src.scenes.stats_scene", fromlist=["StatsScene"])
        except ModuleNotFoundError:
            return None

        scene_class = getattr(module, "StatsScene")
        return scene_class(self.game, self.score_manager, self.stats_tracker)

    def _play_sound(self, sound_name: str) -> None:
        sound_manager = getattr(self.game, "sound_manager", None)
        if sound_manager is None:
            return

        play = getattr(sound_manager, "play", None)
        if callable(play):
            play(sound_name)

    def _opponent_config(self, opponent_id: str | None) -> dict:
        if opponent_id is None:
            return TOURNAMENT_OPPONENTS[0]

        for opponent in TOURNAMENT_OPPONENTS:
            if opponent["id"] == opponent_id:
                return opponent

        return TOURNAMENT_OPPONENTS[0]

    def _player_side_for_score_side(self, score_side: str) -> str:
        return "bottom" if score_side == "p1" else "top"

    def _score_side_for_player_side(self, player_side: str) -> str:
        return "p1" if player_side == "bottom" else "p2"
