"""Cena principal de gameplay da partida."""

from __future__ import annotations

import random
from math import atan2, degrees

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
    BOT_SERVE_DELAY_RANGE,
    BOT_SERVE_MISS_CHANCE,
    CONTROLS_P1,
    CONTROLS_P2,
    COURT_MARGIN_X,
    COURT_MARGIN_Y,
    GREEN_LOCKED,
    HEIGHT,
    HUD_BG,
    LINE_OUTLINE,
    NET_WIDTH,
    NET_X,
    ORANGE,
    OUT_MESSAGE_TIME,
    PLAYER_SPEED,
    RED,
    SERVE_AIM_OSC_SPEED,
    SERVE_AIM_PADDING,
    SERVE_IN_FLIGHT,
    SERVE_MAX_ANGLE,
    SERVE_MESSAGE,
    SERVE_PREPARING,
    SERVE_RALLY,
    SWEET_SPOT_HIGH,
    SWEET_SPOT_LOW,
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
        p1_char = getattr(self.game, "player1_character", None)
        custom_name = getattr(self.game, "player_name", "").strip()
        if custom_name:
            player1_name = custom_name
        elif p1_char:
            player1_name = p1_char["name"]
        else:
            player1_name = "Player 1" if mode == "2p" else "Voce"
        self.player1 = Player(self.game.assets, "left", CONTROLS_P1, player1_name, p1_char)
        self.training_submode = "bot" if mode == "training" else None
        self.rally_count = 0
        self.saved_training_record = self._training_record()
        self.max_rally = self.saved_training_record
        self.player2 = self._build_second_player()
        self.players = self._build_players_group()
        self.score_manager = self._build_score_manager()
        self.stats_tracker = StatsTracker()
        self.ball = Ball(self.game.assets, Vector2(WIDTH / 2, HEIGHT / 2))
        self.last_hit_time = 0
        self.serve_lane = "bottom"
        self.serve_state = SERVE_RALLY
        self.serve_target_rect: pygame.Rect | None = None
        self.serve_auto_timer = 0.0
        self.serve_auto_values: tuple[float, float] | None = None
        self.point_message: str | None = None
        self.point_message_until = 0
        self.pending_point_winner: str | None = None
        self._next_scene = None
        self._match_start_time: int = pygame.time.get_ticks()
        self._hud_font = pygame.font.Font(None, 26)
        self._hud_font.set_bold(True)
        self._score_font = pygame.font.Font(None, 48)
        self._score_font.set_bold(True)
        self._small_font = pygame.font.Font(None, 21)
        self._small_font.set_bold(True)
        self._message_font = pygame.font.Font(None, 86)
        self._message_font.set_bold(True)
        if self.mode == "training":
            self._serve_training_ball()
        else:
            self._start_serve_preparation()
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

            if self._point_message_active():
                continue

            if self.serve_state == SERVE_PREPARING:
                self._handle_serve_event(event)
                continue

            hit_result = self.player1.handle_event(event, self.ball)
            if hit_result == "out_hit":
                loser_side = self._score_side_for_player_side(self.player1.side)
                self._show_out_message(self._other_score_side(loser_side))
                continue
            self._register_hit_result(hit_result, self.player1)
            if self.mode == "2p":
                hit_result = self.player2.handle_event(event, self.ball)
                if hit_result == "out_hit":
                    loser_side = self._score_side_for_player_side(self.player2.side)
                    self._show_out_message(self._other_score_side(loser_side))
                    continue
                self._register_hit_result(hit_result, self.player2)

    def update(self, dt: float) -> None:
        """Atualiza jogadores, bola, colisões e física básica.

        Args:
            dt: Tempo decorrido desde o último quadro, em segundos.
        """
        if self._next_scene is not None:
            return

        if self._update_point_message():
            return

        if self.serve_state == SERVE_PREPARING:
            self._update_serve_preparation(dt)
            return

        self.player1.update(dt, self.ball)
        self._update_second_player(dt)
        self.ball.update(dt)
        if self.ball.is_held():
            return

        if self._update_serve_validation():
            return

        if self._update_net_crossing_out():
            return

        if self.mode != "training" and physics.wall_hit_before_net(self.ball):
            loser_side = self._score_side_for_player_side(self.ball.last_hitter)
            winner_side = self._other_score_side(loser_side)
            self._show_out_message(winner_side)
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
        self._draw_service_target(surface)
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
        self._draw_serve_status(surface)
        self._draw_point_message(surface)

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
            p2_char = getattr(self.game, "player2_character", None)
            p2_name = p2_char["name"] if p2_char else "Player 2"
            return Player(self.game.assets, "right", CONTROLS_P2, p2_name, p2_char)

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

        games_target = getattr(self.game, "games_target_set", 6)
        return ScoreManager(self.player1.name, self.player2.name, games_target_set=games_target)

    def _update_second_player(self, dt: float) -> None:
        if self.player2 is None:
            return

        hit_result = self.player2.update(dt, self.ball)
        if isinstance(hit_result, str):
            self._register_hit_result(hit_result, self.player2)

    def _handle_serve_event(self, event: pygame.event.Event) -> None:
        server = self._serving_player()
        if server is None or isinstance(server, AIPlayer):
            return

        hit_result = server.handle_event(event, self.ball)
        if hit_result == "out_hit":
            receiver_side = self._other_score_side(self.ball.server_side)
            self._show_out_message(receiver_side)
            return
        if hit_result not in ("normal", "winner"):
            return

        self._register_hit_result(hit_result, server)
        self._mark_serve_in_flight()

    def _update_serve_preparation(self, dt: float) -> None:
        server = self._serving_player()
        if server is None:
            return

        receiver = self._receiving_player()
        self._update_receiver_during_serve(receiver, dt)

        if isinstance(server, AIPlayer):
            self.serve_auto_timer -= dt
            if self.serve_auto_timer <= 0:
                self._release_bot_serve(server)
            return

        server.update(dt, self.ball)

    def _update_receiver_during_serve(self, receiver, dt: float) -> None:
        if receiver is None or self.serve_target_rect is None:
            return

        if isinstance(receiver, AIPlayer):
            self._move_ai_receiver_in_return_area(receiver, dt)
        elif isinstance(receiver, Player):
            keys = pygame.key.get_pressed()
            receiver.handle_input(keys, dt)

        self._clamp_player_to_return_area(receiver)

    def _move_ai_receiver_in_return_area(self, receiver, dt: float) -> None:
        if self.serve_target_rect is None or not hasattr(receiver, "pos"):
            return

        target = self._receiver_ready_position(receiver)
        movement = target - receiver.pos
        if movement.length_squared() == 0:
            return

        max_step = PLAYER_SPEED * 0.55 * dt
        if movement.length() <= max_step:
            receiver.pos.update(target)
        else:
            receiver.pos += movement.normalize() * max_step
        receiver.rect.center = (round(receiver.pos.x), round(receiver.pos.y))

    def _clamp_player_to_return_area(self, player) -> None:
        if self.serve_target_rect is None or not hasattr(player, "pos"):
            return

        return_area = self._return_area_rect()
        half_width = player.rect.width / 2
        half_height = player.rect.height / 2
        min_x = return_area.left + half_width
        max_x = return_area.right - half_width
        min_y = return_area.top + half_height
        max_y = return_area.bottom - half_height

        if min_x > max_x:
            min_x = max_x = return_area.centerx
        if min_y > max_y:
            min_y = max_y = return_area.centery

        player.pos.x = max(min_x, min(max_x, player.pos.x))
        player.pos.y = max(min_y, min(max_y, player.pos.y))
        player.rect.center = (round(player.pos.x), round(player.pos.y))
        if hasattr(player, "target_y"):
            player.target_y = player.pos.y

    def _return_area_rect(self) -> pygame.Rect:
        if self.serve_target_rect is None:
            return pygame.Rect(COURT_MARGIN_X, COURT_MARGIN_Y, 0, 0)

        court_top = COURT_MARGIN_Y
        court_bottom = HEIGHT - COURT_MARGIN_Y
        if self.score_manager is None:
            server_side = self.ball.server_side
        else:
            server_side = self.score_manager.server()

        if server_side == "p1":
            x = self.serve_target_rect.right
            width = WIDTH - COURT_MARGIN_X - x
        else:
            x = COURT_MARGIN_X
            width = self.serve_target_rect.left - x

        return pygame.Rect(x, court_top, width, court_bottom - court_top)

    def _receiver_ready_position(self, receiver) -> Vector2:
        if self.serve_target_rect is None:
            return Vector2(receiver.pos)

        half_width = receiver.rect.width / 2
        if receiver.side == "left":
            x = COURT_MARGIN_X + half_width
        else:
            x = WIDTH - COURT_MARGIN_X - half_width

        return Vector2(x, self.serve_target_rect.centery)

    def _release_bot_serve(self, server: AIPlayer) -> None:
        if self.serve_auto_values is None:
            return

        angle, power = self.serve_auto_values
        is_sweet = SWEET_SPOT_LOW <= power <= SWEET_SPOT_HIGH
        self.ball.apply_shot(angle, power, server.side, is_sweet)
        server.timing_bars.reset()
        self._register_hit_result("winner" if is_sweet else "normal", server)
        self._mark_serve_in_flight()

    def _mark_serve_in_flight(self) -> None:
        server_side = self.score_manager.server()
        self.serve_state = SERVE_IN_FLIGHT
        self.ball.was_served = True
        self.ball.server_side = server_side
        self.ball.last_hitter = self._player_side_for_score_side(server_side)
        self.ball.bounce_count = 0
        self.serve_auto_values = None

    def _update_serve_validation(self) -> bool:
        if self.serve_state != SERVE_IN_FLIGHT:
            return False

        if self._serve_touched_vertical_bounds():
            self._handle_invalid_serve()
            return True

        if physics.crossed_net_outside(self.ball):
            self._handle_invalid_serve()
            return True

        if self._serve_hit_target_box():
            self.serve_state = SERVE_RALLY
            self.serve_target_rect = None
            return False

        if self._serve_passed_target_box():
            self._handle_invalid_serve()
            return True

        return False

    def _serve_hit_target_box(self) -> bool:
        if self.serve_target_rect is None:
            return False

        return self.serve_target_rect.collidepoint(self.ball.rect.center)

    def _serve_passed_target_box(self) -> bool:
        if self.serve_target_rect is None:
            return False

        if self.ball.server_side == "p1":
            return self.ball.rect.centerx > self.serve_target_rect.right

        return self.ball.rect.centerx < self.serve_target_rect.left

    def _serve_touched_vertical_bounds(self) -> bool:
        return self.ball.rect.top <= 0 or self.ball.rect.bottom >= HEIGHT

    def _handle_invalid_serve(self) -> None:
        receiver_side = self._other_score_side(self.ball.server_side)
        self._show_out_message(receiver_side)

    def _update_net_crossing_out(self) -> bool:
        crossed_to_side = physics.crossed_net_outside(self.ball)
        if crossed_to_side is None:
            return False

        if self.mode == "training":
            self._reset_training_rally()
            return True

        self._show_out_message(self._net_out_winner(crossed_to_side))
        return True

    def _net_out_winner(self, crossed_to_side: str) -> str:
        loser_player_side = self.ball.last_hitter
        if loser_player_side in ("left", "right"):
            loser_score_side = self._score_side_for_player_side(loser_player_side)
            return self._other_score_side(loser_score_side)

        return "p2" if crossed_to_side == "right" else "p1"

    def _show_out_message(self, winner_side: str) -> None:
        self.ball.velocity.update(0, 0)
        self.ball.release()
        self._reset_all_timing_bars()
        self.serve_state = SERVE_MESSAGE
        self.point_message = "OUT"
        self.pending_point_winner = winner_side
        self.point_message_until = (
            pygame.time.get_ticks() + int(OUT_MESSAGE_TIME * 1000)
        )

    def _point_message_active(self) -> bool:
        return self.point_message is not None

    def _update_point_message(self) -> bool:
        if self.point_message is None:
            return False

        if pygame.time.get_ticks() < self.point_message_until:
            return True

        winner_side = self.pending_point_winner
        self.point_message = None
        self.pending_point_winner = None
        self.serve_state = SERVE_RALLY
        if winner_side is not None:
            self._award_point_to(winner_side)
        return True

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
        self._award_point_to(winner_side)

    def _award_point_to(self, winner_side: str) -> None:
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
        self._advance_serve_lane()
        self._start_serve_preparation()
        self.last_hit_time = pygame.time.get_ticks()

    def _start_serve_preparation(self) -> None:
        server_side = self.score_manager.server()
        server = self._serving_player()
        receiver = self._receiving_player()
        if server is None:
            return

        self._reset_all_timing_bars()
        self.serve_state = SERVE_PREPARING
        self.serve_target_rect = self._service_target_rect(server_side)
        self.serve_auto_values = None
        self.serve_auto_timer = 0.0
        self.point_message = None
        self.point_message_until = 0
        self.pending_point_winner = None

        self._position_players_for_serve(server, receiver)
        self.ball.reset(server_side)
        self.ball.capture_by_player(server)
        self.ball.server_side = server_side
        self.ball.last_hitter = self._player_side_for_score_side(server_side)
        self.ball.last_hit_quality = "normal"
        self.ball.bounce_count = 0
        self.ball.was_served = False

        aim_min, aim_max, aim_center, aim_sweet_range = self._serve_angle_window()
        if isinstance(server, AIPlayer):
            angle, power = self._choose_bot_serve_values()
            server.timing_bars.lock_values(
                angle,
                power,
                aim_min,
                aim_max,
                aim_sweet_range,
            )
            self.serve_auto_values = (angle, power)
            self.serve_auto_timer = random.uniform(*BOT_SERVE_DELAY_RANGE)
        else:
            server.prepare_serve(
                self.ball,
                (aim_min, aim_max),
                aim_center,
                SERVE_AIM_OSC_SPEED,
                aim_sweet_range,
            )
        self.last_hit_time = pygame.time.get_ticks()

    def _position_players_for_serve(self, server, receiver) -> None:
        server_y = self._serve_lane_center_y(self.serve_lane)

        self._place_player_for_serve(server, server.side, server_y)
        if receiver is not None:
            ready_position = self._receiver_ready_position(receiver)
            receiver.pos.update(ready_position)
            receiver.rect.center = (round(receiver.pos.x), round(receiver.pos.y))
            self._clamp_player_to_return_area(receiver)

    def _place_player_for_serve(self, player, side: str, y: float) -> None:
        if not hasattr(player, "pos"):
            return

        half_width = player.rect.width / 2
        if side == "left":
            x = COURT_MARGIN_X + half_width
        else:
            x = WIDTH - COURT_MARGIN_X - half_width

        player.pos.update(x, y)
        player.rect.center = (round(player.pos.x), round(player.pos.y))

    def _service_target_rect(self, server_side: str) -> pygame.Rect:
        court_left = COURT_MARGIN_X
        court_right = WIDTH - COURT_MARGIN_X
        court_top = COURT_MARGIN_Y
        court_bottom = HEIGHT - COURT_MARGIN_Y
        center_y = HEIGHT // 2
        left_service_x = (court_left + NET_X) // 2
        right_service_x = (NET_X + court_right) // 2
        target_lane = self._opposite_serve_lane(self.serve_lane)

        if target_lane == "top":
            y = court_top
            height = center_y - court_top
        else:
            y = center_y
            height = court_bottom - center_y

        if server_side == "p1":
            x = NET_X + NET_WIDTH // 2
            width = right_service_x - x
        else:
            x = left_service_x
            width = NET_X - NET_WIDTH // 2 - x

        return pygame.Rect(round(x), round(y), round(width), round(height))

    def _serve_angle_window(
        self,
    ) -> tuple[float, float, float, tuple[float, float]]:
        if self.serve_target_rect is None:
            return -SERVE_MAX_ANGLE, SERVE_MAX_ANGLE, 0.0, (0.0, 0.0)

        origin = Vector2(self.ball.rect.center)
        corners = (
            self.serve_target_rect.topleft,
            self.serve_target_rect.topright,
            self.serve_target_rect.bottomleft,
            self.serve_target_rect.bottomright,
            self.serve_target_rect.center,
        )
        angles = [
            self._angle_from_ball_to_point(origin, Vector2(point))
            for point in corners
        ]
        sweet_min = min(angles)
        sweet_max = max(angles)
        aim_min = max(-SERVE_MAX_ANGLE, sweet_min - SERVE_AIM_PADDING)
        aim_max = min(SERVE_MAX_ANGLE, sweet_max + SERVE_AIM_PADDING)
        aim_center = self._angle_from_ball_to_point(
            origin,
            Vector2(self.serve_target_rect.center),
        )
        aim_center = max(aim_min, min(aim_max, aim_center))
        return aim_min, aim_max, aim_center, (sweet_min, sweet_max)

    def _angle_from_ball_to_point(self, origin: Vector2, target: Vector2) -> float:
        direction_x = 1 if self.ball.server_side == "p1" else -1
        dx = (target.x - origin.x) * direction_x
        dy = target.y - origin.y
        return degrees(atan2(dy, max(1.0, dx)))

    def _choose_bot_serve_values(self) -> tuple[float, float]:
        if self.serve_target_rect is None:
            return 0.0, 0.75

        target = self.serve_target_rect.inflate(-56, -56)
        if target.width <= 0 or target.height <= 0:
            target = self.serve_target_rect

        if random.random() < BOT_SERVE_MISS_CHANCE:
            target_point = self._random_missed_serve_target()
        else:
            target_point = Vector2(
                random.uniform(target.left, target.right),
                random.uniform(target.top, target.bottom),
            )

        origin = Vector2(self.ball.rect.center)
        angle = self._angle_from_ball_to_point(origin, target_point)
        power = random.uniform(0.72, 0.88)
        return angle, power

    def _random_missed_serve_target(self) -> Vector2:
        if self.serve_target_rect is None:
            return Vector2(WIDTH / 2, HEIGHT / 2)

        wrong_lane = self.serve_lane
        wrong_y = self._serve_lane_center_y(wrong_lane)
        wrong_y += random.uniform(-45, 45)
        if self.ball.server_side == "p1":
            x = random.uniform(NET_X + 20, WIDTH - COURT_MARGIN_X)
        else:
            x = random.uniform(COURT_MARGIN_X, NET_X - 20)

        return Vector2(x, wrong_y)

    def _serve_lane_center_y(self, lane: str) -> float:
        center_y = HEIGHT / 2
        if lane == "top":
            return (COURT_MARGIN_Y + center_y) / 2

        return (center_y + HEIGHT - COURT_MARGIN_Y) / 2

    def _opposite_serve_lane(self, lane: str) -> str:
        return "bottom" if lane == "top" else "top"

    def _advance_serve_lane(self) -> None:
        self.serve_lane = self._opposite_serve_lane(self.serve_lane)

    def _reset_all_timing_bars(self) -> None:
        self.player1.timing_bars.reset()
        if self.player2 is not None and hasattr(self.player2, "timing_bars"):
            self.player2.timing_bars.reset()

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

        if self.ball.rect.right < WIDTH - COURT_MARGIN_X or self.ball.velocity.x <= 0:
            return False

        self.ball.rect.right = WIDTH - COURT_MARGIN_X
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

    def _serve_training_ball(self) -> None:
        self.ball.pos.update(WIDTH / 2, HEIGHT / 2)
        self.ball.previous_pos.update(self.ball.pos)
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

        if self.mode == "1p":
            elapsed = pygame.time.get_ticks() - self._match_start_time
            self.game.tournament_time_ms = (
                getattr(self.game, "tournament_time_ms", 0) + elapsed
            )

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

    def _serving_player(self):
        if self.score_manager is None:
            return None

        return self.player1 if self.score_manager.server() == "p1" else self.player2

    def _receiving_player(self):
        if self.score_manager is None:
            return None

        return self.player2 if self.score_manager.server() == "p1" else self.player1

    def _other_score_side(self, score_side: str) -> str:
        return "p2" if score_side == "p1" else "p1"

    def _training_record(self) -> int:
        highscore_manager = getattr(self.game, "highscore_manager", None)
        if highscore_manager is None:
            return 0

        records = highscore_manager.get_top("training")
        values = [record.get("maior_rally", 0) for record in records]
        return max((int(value) for value in values if str(value).isdigit()), default=0)

    def _draw_service_target(self, surface: pygame.Surface) -> None:
        if self.serve_target_rect is None:
            return

        if self.serve_state not in (SERVE_PREPARING, SERVE_IN_FLIGHT):
            return

        rect = self.serve_target_rect
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill((255, 220, 60, 54))
        surface.blit(overlay, rect)
        pygame.draw.rect(surface, LINE_OUTLINE, rect, width=5, border_radius=5)
        pygame.draw.rect(
            surface,
            YELLOW,
            rect.inflate(-4, -4),
            width=3,
            border_radius=4,
        )

    def _draw_serve_status(self, surface: pygame.Surface) -> None:
        if self.serve_state != SERVE_PREPARING:
            return

        server = self._serving_player()
        if server is None:
            return

        if isinstance(server, AIPlayer):
            text = "SAQUE DO BOT"
        else:
            bars = getattr(server, "timing_bars", None)
            if bars is not None and bars.state == bars.STATE_POWERING:
                text = "SAQUE: FORCA"
            else:
                text = "SAQUE: ANGULO"

        self._draw_text_with_outline(
            surface,
            text,
            self._hud_font,
            (WIDTH // 2, 108),
            WHITE,
            LINE_OUTLINE,
        )

    def _draw_point_message(self, surface: pygame.Surface) -> None:
        if self.point_message is None:
            return

        self._draw_text_with_outline(
            surface,
            self.point_message,
            self._message_font,
            (WIDTH // 2, HEIGHT // 2),
            RED,
            LINE_OUTLINE,
        )

    def _draw_text_with_outline(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        center: tuple[int, int],
        color: tuple[int, int, int],
        outline_color: tuple[int, int, int],
    ) -> None:
        outline = font.render(text, True, outline_color)
        fill = font.render(text, True, color)
        outline_rect = outline.get_rect(center=center)
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            surface.blit(outline, outline_rect.move(dx, dy))
        surface.blit(fill, fill.get_rect(center=center))

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
