"""Cena principal de gameplay da partida."""

from __future__ import annotations

import pygame
from pygame.math import Vector2

from src.assets_generator import make_court
from src.entities.ai_player import AIPlayer
from src.entities.ball import Ball
from src.entities.player import Player
from src.entities.practice_bot import PracticeBot
from src.scenes.base_scene import BaseScene
from src.settings import (
    BALL_BASE_SPEED,
    BLACK,
    CONTROLS_P1,
    CONTROLS_P2,
    COURT_MARGIN,
    GREEN_LOCKED,
    HEIGHT,
    HUD_BG,
    LINE_OUTLINE,
    ORANGE,
    TOURNAMENT_OPPONENTS,
    WHITE,
    WIDTH,
    YELLOW,
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
        player1: Jogador da metade esquerda da quadra.
        player2: Jogador ou IA da metade direita da quadra.
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
        player1_name = "Player 1" if mode == "2p" else "Voce"
        self.player1 = Player(self.game.assets, "left", CONTROLS_P1, player1_name)
        self.training_submode = "bot" if mode == "training" else None
        self.rally_count = 0
        self.saved_training_record = self._training_record()
        self.max_rally = self.saved_training_record
        self.player2 = self._build_second_player()
        self.players = self._build_players_group()
        self.score_manager = self._build_score_manager()
        self.stats_tracker = StatsTracker()
        self.ball = Ball(self.game.assets, Vector2(WIDTH / 2, HEIGHT / 2))
        if self.mode == "training":
            self._serve_training_ball()
        else:
            self._serve_ball()
        self.last_hit_time = 0
        self._next_scene = None
        self._hud_font = pygame.font.Font(None, 26)
        self._hud_font.set_bold(True)
        self._score_font = pygame.font.Font(None, 48)
        self._score_font.set_bold(True)
        self._small_font = pygame.font.Font(None, 21)
        self._small_font.set_bold(True)
        self._play_music(self.scenery)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa eventos de gameplay e repassa travas ao jogador humano.

        Args:
            events: Lista de eventos capturados no quadro atual.
        """
        for event in events:
            if (
                self.mode == "training"
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_TAB
            ):
                self._toggle_training_submode()
                return

            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE,
                pygame.K_p,
            ):
                self._next_scene = self._build_pause_scene()
                return

            hit_result = self.player1.handle_event(event, self.ball)
            self._register_hit_result(hit_result, self.player1)
            if self.mode == "2p":
                hit_result = self.player2.handle_event(event, self.ball)
                self._register_hit_result(hit_result, self.player2)

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
        if self.ball.is_held():
            return

        if physics.bounce_off_walls(self.ball):
            self.ball.bounce_count += 1
            self._play_sound("bounce")
        if self._bounce_training_wall():
            self.ball.bounce_count += 1
            self._play_sound("bounce")

        out_side = physics.is_out_of_bounds(self.ball)
        if out_side is not None:
            if self.mode == "training":
                self._reset_training_rally()
                return

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
        if self.player2 is not None:
            surface.blit(self.player2.image, self.player2.rect)
        self.player1.draw_aim_arrow(surface, self.ball)
        if self.player2 is not None and hasattr(self.player2, "draw_aim_arrow"):
            self.player2.draw_aim_arrow(surface, self.ball)
        surface.blit(self.ball.image, self.ball.rect)
        self.player1.timing_bars.draw(surface)
        if self.player2 is not None and hasattr(self.player2, "timing_bars"):
            self.player2.timing_bars.draw(surface)
        self.draw_hud(surface)

    def draw_hud(self, surface: pygame.Surface) -> None:
        """Desenha placar, games, sets e sacador no topo da partida.

        Args:
            surface: Superfície principal onde a HUD deve ser renderizada.
        """
        if self.mode == "training":
            self._draw_training_hud(surface)
            return

        panel_rect = pygame.Rect(18, 12, WIDTH - 36, 74)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        local_rect = panel.get_rect()
        pygame.draw.rect(panel, HUD_BG, local_rect, border_radius=14)
        pygame.draw.rect(panel, LINE_OUTLINE, local_rect, width=4, border_radius=14)
        surface.blit(panel, panel_rect)

        self._draw_player_names(surface, panel_rect)
        self._draw_game_score(surface, panel_rect)
        self._draw_games_and_sets(surface, panel_rect)
        self._draw_server_indicator(surface, panel_rect)
        if self.score_manager.is_tiebreak():
            self._draw_tiebreak_badge(surface, panel_rect)

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
            return AIPlayer(self.game.assets, "right", self.opponent_config)

        if self.mode == "2p":
            return Player(self.game.assets, "right", CONTROLS_P2, "Player 2")

        if self.mode == "training" and self.training_submode == "bot":
            return PracticeBot(self.game.assets)

        if self.mode == "training":
            return None

        return Player(self.game.assets, "right", CONTROLS_P2, "Jogador 2")

    def _build_players_group(self) -> pygame.sprite.Group:
        sprites = [self.player1]
        if self.player2 is not None:
            sprites.append(self.player2)
        return pygame.sprite.Group(*sprites)

    def _build_score_manager(self) -> ScoreManager | None:
        if self.mode == "training":
            return None

        return ScoreManager(self.player1.name, self.player2.name)

    def _update_second_player(self, dt: float) -> None:
        if self.player2 is None:
            return

        hit_result = self.player2.update(dt, self.ball)
        if isinstance(hit_result, str):
            self._register_hit_result(hit_result, self.player2)

    def _handle_player_collision(self, player: Player) -> None:
        if self.ball.is_held():
            return

        if not player_hits_ball(player, self.ball, self.last_hit_time):
            return

        if player.capture_ball(self.ball):
            self.last_hit_time = pygame.time.get_ticks()

    def _register_hit_result(self, hit_result: str, player: Player) -> None:
        if hit_result not in ("normal", "winner"):
            return

        self.last_hit_time = pygame.time.get_ticks()
        self.ball.last_hit_quality = hit_result
        self.ball.last_hitter = player.side
        self._play_sound("hit")
        if self.mode == "training":
            if player is self.player1:
                self.rally_count += 1
                self.max_rally = max(self.max_rally, self.rally_count)
            return

        if self._score_side_for_player_side(player.side) != self.ball.server_side:
            self.ball.was_served = False

    def _award_point(self, out_side: str) -> None:
        winner_side = "p1" if out_side == "right" else "p2"
        point_type = self._point_type_for(winner_side)
        self.score_manager.add_point(winner_side, point_type)
        self._register_point_stat(winner_side, point_type)
        self._play_sound("ace" if point_type == "ace" else "score")

        if self.score_manager.is_match_over():
            self._freeze_match()
            self._stop_music()
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

    def _reset_training_rally(self) -> None:
        self._save_training_record_if_needed()
        self.rally_count = 0
        self._serve_training_ball()
        self.player1.timing_bars.reset()
        self.last_hit_time = pygame.time.get_ticks()

    def _toggle_training_submode(self) -> None:
        if self.mode != "training":
            return

        self.training_submode = "wall" if self.training_submode == "bot" else "bot"
        self.player2 = self._build_second_player()
        self.players = self._build_players_group()
        self.rally_count = 0
        self._serve_training_ball()
        self.player1.timing_bars.reset()
        self._play_sound("menu_click")

    def _bounce_training_wall(self) -> bool:
        if self.mode != "training" or self.training_submode != "wall":
            return False

        if self.ball.rect.right < WIDTH - COURT_MARGIN or self.ball.velocity.x <= 0:
            return False

        self.ball.rect.right = WIDTH - COURT_MARGIN
        self.ball.pos.x = self.ball.rect.centerx
        self.ball.velocity.x = -abs(self.ball.velocity.x)
        return True

    def _save_training_record_if_needed(self) -> None:
        if self.max_rally <= self.saved_training_record:
            return

        highscore_manager = getattr(self.game, "highscore_manager", None)
        if highscore_manager is None:
            return

        highscore_manager.add_training_record(self.player1.name, self.max_rally)
        self.saved_training_record = self.max_rally

    def _serve_ball(self) -> None:
        server_side = self.score_manager.server()
        player_side = self._player_side_for_score_side(server_side)
        direction_x = 1 if server_side == "p1" else -1
        self.ball.velocity.update(BALL_BASE_SPEED * direction_x, 0)
        self.ball.release()
        self.ball.server_side = server_side
        self.ball.was_served = True
        self.ball.last_hitter = player_side
        self.ball.last_hit_quality = "normal"
        self.ball.bounce_count = 0

    def _serve_training_ball(self) -> None:
        self.ball.pos.update(WIDTH / 2, HEIGHT / 2)
        self.ball.rect.center = (round(self.ball.pos.x), round(self.ball.pos.y))
        self.ball.velocity.update(BALL_BASE_SPEED, 0)
        self.ball.release()
        self.ball.server_side = "training"
        self.ball.was_served = False
        self.ball.last_hitter = None
        self.ball.last_hit_quality = "normal"
        self.ball.bounce_count = 0

    def _freeze_match(self) -> None:
        self.ball.velocity.update(0, 0)
        self.player1.timing_bars.reset()
        if self.player2 is not None and hasattr(self.player2, "timing_bars"):
            self.player2.timing_bars.reset()

    def _build_stats_scene(self):
        try:
            module = __import__("src.scenes.stats_scene", fromlist=["StatsScene"])
        except ModuleNotFoundError:
            return None

        scene_class = getattr(module, "StatsScene")
        return scene_class(
            self.game,
            self.score_manager,
            self.stats_tracker,
            self.mode,
        )

    def _build_pause_scene(self):
        module = __import__("src.scenes.pause_scene", fromlist=["PauseScene"])
        scene_class = getattr(module, "PauseScene")
        return scene_class(self.game, self)

    def _play_sound(self, sound_name: str) -> None:
        sound_manager = getattr(self.game, "sound_manager", None)
        if sound_manager is None:
            return

        play = getattr(sound_manager, "play", None)
        if callable(play):
            play(sound_name)

    def _play_music(self, scenery_id: str) -> None:
        sound_manager = getattr(self.game, "sound_manager", None)
        if sound_manager is None:
            return

        play_music = getattr(sound_manager, "play_music", None)
        if callable(play_music):
            play_music(scenery_id)

    def _stop_music(self) -> None:
        sound_manager = getattr(self.game, "sound_manager", None)
        if sound_manager is None:
            return

        stop_music = getattr(sound_manager, "stop_music", None)
        if callable(stop_music):
            stop_music()

    def _opponent_config(self, opponent_id: str | None) -> dict:
        if opponent_id is None:
            return TOURNAMENT_OPPONENTS[0]

        for opponent in TOURNAMENT_OPPONENTS:
            if opponent["id"] == opponent_id:
                return opponent

        return TOURNAMENT_OPPONENTS[0]

    def _player_side_for_score_side(self, score_side: str) -> str:
        return "left" if score_side == "p1" else "right"

    def _score_side_for_player_side(self, player_side: str) -> str:
        return "p1" if player_side == "left" else "p2"

    def _training_record(self) -> int:
        highscore_manager = getattr(self.game, "highscore_manager", None)
        if highscore_manager is None:
            return 0

        records = highscore_manager.get_top("training")
        values = [record.get("maior_rally", 0) for record in records]
        return max((int(value) for value in values if str(value).isdigit()), default=0)

    def _draw_player_names(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
    ) -> None:
        p1_text = self._hud_font.render(self.score_manager.p1_name, True, WHITE)
        p2_text = self._hud_font.render(self.score_manager.p2_name, True, WHITE)
        surface.blit(p1_text, (panel_rect.left + 44, panel_rect.top + 13))
        surface.blit(p2_text, (panel_rect.left + 44, panel_rect.top + 42))

    def _draw_game_score(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
    ) -> None:
        p1_score, p2_score = self.score_manager.current_game_score()
        score_text = self._score_font.render(
            f"{p1_score} - {p2_score}",
            True,
            WHITE,
        )
        surface.blit(score_text, score_text.get_rect(center=panel_rect.center))

    def _draw_games_and_sets(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
    ) -> None:
        games = self.score_manager.current_set_games()
        game_text = self._hud_font.render(
            f"Games {games[0]} - {games[1]}",
            True,
            WHITE,
        )
        surface.blit(game_text, (panel_rect.right - 205, panel_rect.top + 13))
        self._draw_set_dots(surface, panel_rect)

    def _draw_set_dots(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
    ) -> None:
        p1_sets, p2_sets = self.score_manager.sets_won()
        base_x = panel_rect.right - 156
        y_positions = (panel_rect.top + 48, panel_rect.top + 63)

        for row, sets_won in enumerate((p1_sets, p2_sets)):
            label = self._small_font.render(f"P{row + 1}", True, WHITE)
            surface.blit(label, (base_x - 38, y_positions[row] - 9))
            for index in range(2):
                color = GREEN_LOCKED if index < sets_won else WHITE
                center = (base_x + index * 22, y_positions[row])
                pygame.draw.circle(surface, BLACK, center, 8)
                pygame.draw.circle(surface, color, center, 5)

    def _draw_server_indicator(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
    ) -> None:
        if self.score_manager.server() == "p1":
            y = panel_rect.top + 24
        else:
            y = panel_rect.top + 53
        center = (panel_rect.left + 25, y)
        pygame.draw.circle(surface, BLACK, center, 9)
        pygame.draw.circle(surface, YELLOW, center, 6)

    def _draw_tiebreak_badge(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
    ) -> None:
        badge_rect = pygame.Rect(0, 0, 120, 24)
        badge_rect.center = (panel_rect.centerx, panel_rect.bottom - 12)
        pygame.draw.rect(surface, BLACK, badge_rect, border_radius=8)
        pygame.draw.rect(
            surface,
            ORANGE,
            badge_rect.inflate(-4, -4),
            border_radius=6,
        )
        text = self._small_font.render("TIE-BREAK", True, BLACK)
        surface.blit(text, text.get_rect(center=badge_rect.center))

    def _draw_training_hud(self, surface: pygame.Surface) -> None:
        panel_rect = pygame.Rect(18, 12, WIDTH - 36, 64)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        local_rect = panel.get_rect()
        pygame.draw.rect(panel, HUD_BG, local_rect, border_radius=14)
        pygame.draw.rect(panel, LINE_OUTLINE, local_rect, width=4, border_radius=14)
        surface.blit(panel, panel_rect)

        submode = "PAREDE" if self.training_submode == "wall" else "BOT"
        record = max(self.max_rally, self._training_record())
        label = self._hud_font.render(f"TREINO: {submode}", True, WHITE)
        rally = self._score_font.render(f"RALLY: {self.rally_count}", True, WHITE)
        record_text = self._hud_font.render(f"RECORDE: {record}", True, WHITE)
        surface.blit(label, (panel_rect.left + 34, panel_rect.top + 22))
        surface.blit(rally, rally.get_rect(center=panel_rect.center))
        surface.blit(
            record_text,
            record_text.get_rect(midright=(panel_rect.right - 34, panel_rect.centery)),
        )
