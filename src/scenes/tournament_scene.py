"""Cena de mapa do torneio progressivo."""

from __future__ import annotations

import pygame

from src.assets_generator import make_ai_sprite, make_button, make_trophy
from src.scenes.base_scene import BaseScene
from src.scenes.menu_scene import MenuScene
from src.settings import (
    BLACK,
    BLUE,
    GRAY_INACTIVE,
    GREEN_LOCKED,
    HEIGHT,
    LINE_OUTLINE,
    ORANGE,
    TOURNAMENT_OPPONENTS,
    WHITE,
    WIDTH,
    YELLOW,
)


class TournamentScene(BaseScene):
    """Mostra o progresso do torneio e os tres adversarios.

    Args:
        game: Instancia principal do jogo, que armazena
            `tournament_progress`.

    Attributes:
        selected_index: Card atualmente selecionado para ver detalhes.
    """

    DESCRIPTIONS = {
        "beach": "Primeira fase: golpes leves e tempo de reacao generoso.",
        "forest": "Segunda fase: movimentacao melhor e mira menos previsivel.",
        "stadium": "Final: reacoes rapidas e bolas muito bem colocadas.",
    }

    def __init__(self, game) -> None:
        """Inicializa selecao e fontes da tela de torneio."""
        super().__init__(game)
        progress = self._progress()
        self.selected_index = min(progress, len(TOURNAMENT_OPPONENTS) - 1)
        self._next_scene = None
        self._message_timer = 0.0
        self._title_font = pygame.font.Font(None, 62)
        self._name_font = pygame.font.Font(None, 34)
        self._body_font = pygame.font.Font(None, 25)
        self._small_font = pygame.font.Font(None, 22)
        self._hint_font = pygame.font.Font(None, 26)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa navegacao, retorno ao menu e inicio de partida.

        Args:
            events: Lista de eventos capturados pelo Pygame neste quadro.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self._next_scene = MenuScene(self.game)
            elif event.key == pygame.K_LEFT:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_RIGHT:
                last_index = len(TOURNAMENT_OPPONENTS) - 1
                self.selected_index = min(last_index, self.selected_index + 1)
            elif event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
                self._activate()

    def update(self, dt: float) -> None:
        """Atualiza temporizadores visuais simples.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.
        """
        self._message_timer = max(0.0, self._message_timer - dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha mapa do torneio, cards e estado de progresso.

        Args:
            surface: Superficie principal onde a cena deve ser desenhada.
        """
        surface.fill(YELLOW)
        self._draw_background(surface)
        self._draw_title(surface)

        if self._progress() >= len(TOURNAMENT_OPPONENTS):
            self._draw_completed_tournament(surface)
        else:
            self._draw_cards(surface)
            self._draw_detail_panel(surface)

        self._draw_hint(surface)

    def next_scene(self):
        """Retorna a proxima cena solicitada.

        Returns:
            MenuScene, GameplayScene quando disponivel, ou None para continuar.
        """
        next_scene = self._next_scene
        self._next_scene = None
        return next_scene

    def _activate(self) -> None:
        progress = self._progress()

        if progress >= len(TOURNAMENT_OPPONENTS):
            self._next_scene = MenuScene(self.game)
            return

        opponent = TOURNAMENT_OPPONENTS[progress]
        gameplay_scene = self._build_gameplay_scene(opponent["id"])
        if gameplay_scene is None:
            self._message_timer = 2.0
            return

        self._next_scene = gameplay_scene

    def _build_gameplay_scene(self, opponent_id: str):
        try:
            module = __import__("src.scenes.gameplay_scene", fromlist=["GameplayScene"])
        except ModuleNotFoundError:
            return None

        scene_class = getattr(module, "GameplayScene")
        return scene_class(self.game, mode="1p", opponent_id=opponent_id)

    def _progress(self) -> int:
        progress = getattr(self.game, "tournament_progress", 0)
        return max(0, min(progress, len(TOURNAMENT_OPPONENTS)))

    def _draw_background(self, surface: pygame.Surface) -> None:
        track_y = 302
        pygame.draw.line(surface, WHITE, (180, track_y), (780, track_y), 10)
        pygame.draw.line(surface, BLACK, (180, track_y), (780, track_y), 4)
        pygame.draw.circle(surface, BLUE, (74, 72), 26)
        pygame.draw.circle(surface, BLACK, (74, 72), 26, width=4)
        pygame.draw.circle(surface, ORANGE, (WIDTH - 74, 72), 26)
        pygame.draw.circle(surface, BLACK, (WIDTH - 74, 72), 26, width=4)

    def _draw_title(self, surface: pygame.Surface) -> None:
        self._draw_outlined_text(
            surface,
            "TORNEIO",
            self._title_font,
            (WIDTH // 2, 66),
            WHITE,
        )

    def _draw_cards(self, surface: pygame.Surface) -> None:
        card_width = 250
        card_height = 250
        gap = 28
        start_x = (WIDTH - card_width * 3 - gap * 2) // 2
        y = 142

        for index, opponent in enumerate(TOURNAMENT_OPPONENTS):
            x = start_x + index * (card_width + gap)
            rect = pygame.Rect(x, y, card_width, card_height)
            self._draw_card(surface, rect, index, opponent)

    def _draw_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        index: int,
        opponent: dict,
    ) -> None:
        progress = self._progress()
        selected = index == self.selected_index
        fill = WHITE if selected else (245, 245, 245)
        outline = ORANGE if selected else BLACK

        pygame.draw.rect(surface, fill, rect, border_radius=12)
        pygame.draw.rect(surface, outline, rect, width=5, border_radius=12)

        sprite = self.game.assets.get(
            ("ai_sprite", opponent["id"]),
            lambda opponent_id=opponent["id"]: make_ai_sprite(opponent_id),
        )
        sprite_rect = sprite.get_rect(center=(rect.centerx, rect.top + 70))
        surface.blit(sprite, sprite_rect)

        name = self._name_font.render(opponent["name"], True, BLACK)
        surface.blit(name, name.get_rect(center=(rect.centerx, rect.top + 126)))

        description = self.DESCRIPTIONS[opponent["id"]]
        self._draw_wrapped_text(
            surface,
            description,
            rect.inflate(-28, 0),
            rect.top + 150,
        )
        self._draw_status(surface, rect, index, progress)

    def _draw_status(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        index: int,
        progress: int,
    ) -> None:
        status_rect = pygame.Rect(rect.centerx - 72, rect.bottom - 52, 144, 34)

        if index < progress:
            pygame.draw.rect(surface, GREEN_LOCKED, status_rect, border_radius=10)
            pygame.draw.rect(surface, BLACK, status_rect, width=3, border_radius=10)
            self._draw_check(surface, status_rect.center)
        elif index == progress:
            button = self.game.assets.get(
                ("button", "JOGAR", ORANGE, 144, 34),
                lambda: make_button("JOGAR", ORANGE, 144, 34),
            )
            surface.blit(button, status_rect)
        else:
            pygame.draw.rect(surface, GRAY_INACTIVE, status_rect, border_radius=10)
            pygame.draw.rect(surface, BLACK, status_rect, width=3, border_radius=10)
            self._draw_lock(surface, status_rect.center)

    def _draw_detail_panel(self, surface: pygame.Surface) -> None:
        opponent = TOURNAMENT_OPPONENTS[self.selected_index]
        panel = pygame.Rect(130, 425, WIDTH - 260, 92)
        pygame.draw.rect(surface, WHITE, panel, border_radius=12)
        pygame.draw.rect(surface, LINE_OUTLINE, panel, width=4, border_radius=12)

        detail = (
            f"{opponent['name']} | Reacao {opponent['reaction']:.2f}s | "
            f"Erro de mira {opponent['aim_error']:.1f} | "
            f"Velocidade {opponent['max_speed']}"
        )
        text = self._body_font.render(detail, True, BLACK)
        surface.blit(text, text.get_rect(center=(WIDTH // 2, panel.centery - 16)))

        progress = self._progress()
        if self._message_timer > 0:
            line = "GameplayScene ainda nao foi criada nas proximas tarefas."
        elif self.selected_index == progress:
            line = "ENTER ou ESPACO inicia o proximo jogo do torneio."
        else:
            line = "Use esquerda e direita para comparar os adversarios."

        rendered = self._small_font.render(line, True, BLACK)
        rendered_rect = rendered.get_rect(center=(WIDTH // 2, panel.centery + 18))
        surface.blit(rendered, rendered_rect)

    def _draw_completed_tournament(self, surface: pygame.Surface) -> None:
        trophy = self.game.assets.get("trophy", make_trophy)
        surface.blit(trophy, trophy.get_rect(center=(WIDTH // 2, 230)))

        text = self._name_font.render("Torneio completo!", True, BLACK)
        surface.blit(text, text.get_rect(center=(WIDTH // 2, 326)))

        button = self.game.assets.get(
            ("button", "VOLTAR AO MENU", ORANGE, 260, 48),
            lambda: make_button("VOLTAR AO MENU", ORANGE, 260, 48),
        )
        surface.blit(button, button.get_rect(center=(WIDTH // 2, 400)))

    def _draw_hint(self, surface: pygame.Surface) -> None:
        hint = self._hint_font.render(
            "← → detalhes   ENTER/ESPAÇO jogar   ESC voltar",
            True,
            BLACK,
        )
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    def _draw_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        rect: pygame.Rect,
        y: int,
    ) -> None:
        words = text.split()
        lines: list[str] = []
        current_line = ""

        for word in words:
            candidate = f"{current_line} {word}".strip()
            if self._small_font.size(candidate)[0] <= rect.width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        for line in lines[:3]:
            rendered = self._small_font.render(line, True, BLACK)
            surface.blit(rendered, rendered.get_rect(center=(rect.centerx, y)))
            y += 22

    def _draw_check(self, surface: pygame.Surface, center: tuple[int, int]) -> None:
        x, y = center
        pygame.draw.line(surface, BLACK, (x - 22, y), (x - 7, y + 13), 8)
        pygame.draw.line(surface, BLACK, (x - 7, y + 13), (x + 24, y - 15), 8)
        pygame.draw.line(surface, WHITE, (x - 22, y), (x - 7, y + 13), 4)
        pygame.draw.line(surface, WHITE, (x - 7, y + 13), (x + 24, y - 15), 4)

    def _draw_lock(self, surface: pygame.Surface, center: tuple[int, int]) -> None:
        x, y = center
        shackle_rect = pygame.Rect(x - 16, y - 20, 32, 28)
        pygame.draw.arc(surface, BLACK, shackle_rect, 3.14, 6.28, 5)
        body = pygame.Rect(x - 20, y - 3, 40, 24)
        pygame.draw.rect(surface, BLACK, body, border_radius=6)
        pygame.draw.rect(surface, WHITE, body.inflate(-8, -8), border_radius=4)

    def _draw_outlined_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        text_rect = font.render(text, True, color).get_rect(center=center)
        for offset_x, offset_y in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            outline = font.render(text, True, BLACK)
            surface.blit(outline, text_rect.move(offset_x, offset_y))

        rendered = font.render(text, True, color)
        surface.blit(rendered, text_rect)
