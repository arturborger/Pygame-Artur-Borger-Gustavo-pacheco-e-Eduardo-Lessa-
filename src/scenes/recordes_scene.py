"""Cena de ranking do torneio ordenado pelo menor tempo de conclusao."""

from __future__ import annotations

import pygame

from src.scenes.base_scene import BaseScene
from src.settings import BLACK, BLUE, GREEN_LOCKED, HEIGHT, ORANGE, WHITE, WIDTH, YELLOW

_COL_RANK_X_RATIO = 0.08
_COL_NAME_X_RATIO = 0.18
_COL_TIME_X_RATIO = 0.62
_COL_DATE_X_RATIO = 0.86
_TABLE_LEFT_RATIO = 0.10
_TABLE_RIGHT_RATIO = 0.90


class RecordesScene(BaseScene):
    """Exibe o ranking do torneio ordenado pelo menor tempo de conclusao.

    Apenas partidas concluidas (todos os 3 adversarios vencidos) aparecem
    nesta lista. Quanto menor o tempo, melhor a posicao.

    Args:
        game: Instancia principal do jogo.
    """

    def __init__(self, game) -> None:
        """Inicializa a cena carregando os recordes salvos."""
        super().__init__(game)
        self._records = self._load_records()
        self._next_scene = None
        self._title_font = pygame.font.Font(None, 72)
        self._title_font.set_bold(True)
        self._header_font = pygame.font.Font(None, 32)
        self._header_font.set_bold(True)
        self._row_font = pygame.font.Font(None, 34)
        self._hint_font = pygame.font.Font(None, 30)
        self._empty_font = pygame.font.Font(None, 36)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa retorno ao menu principal.

        Args:
            events: Lista de eventos capturados no quadro atual.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE,
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                from src.scenes.menu_scene import MenuScene
                self._next_scene = MenuScene(self.game)

    def update(self, dt: float) -> None:
        """Mantem a cena estatica.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, sem uso nesta cena.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha a tabela de ranking do torneio.

        Args:
            surface: Superficie principal onde a cena deve renderizar.
        """
        surface.fill(YELLOW)
        self._draw_background(surface)
        self._draw_title(surface)
        self._draw_table(surface)
        self._draw_hint(surface)

    def next_scene(self) -> object:
        """Retorna ao menu quando solicitado.

        Returns:
            MenuScene ou None enquanto o jogador nao pressionar uma tecla.
        """
        ns = self._next_scene
        self._next_scene = None
        return ns

    def _load_records(self) -> list[dict]:
        """Carrega os recordes de torneio do gerenciador de highscores.

        Returns:
            Lista de registros ja ordenados do melhor para o pior.
        """
        highscore_manager = getattr(self.game, "highscore_manager", None)
        if highscore_manager is None:
            return []
        return highscore_manager.get_top("tournament")

    def _draw_background(self, surface: pygame.Surface) -> None:
        table_left = int(WIDTH * _TABLE_LEFT_RATIO)
        table_right = int(WIDTH * _TABLE_RIGHT_RATIO)
        panel = pygame.Rect(table_left - 20, 108, table_right - table_left + 40, HEIGHT - 150)
        pygame.draw.rect(surface, WHITE, panel, border_radius=18)
        pygame.draw.rect(surface, BLACK, panel, width=4, border_radius=18)
        pygame.draw.circle(surface, ORANGE, (148, 76), 34)
        pygame.draw.circle(surface, BLACK, (148, 76), 34, width=4)
        pygame.draw.circle(surface, BLUE, (WIDTH - 148, 76), 34)
        pygame.draw.circle(surface, BLACK, (WIDTH - 148, 76), 34, width=4)

    def _draw_title(self, surface: pygame.Surface) -> None:
        title = "RECORDES — TORNEIO"
        offsets = [(-3, 0), (3, 0), (0, -3), (0, 3)]
        center = (WIDTH // 2, 66)
        for dx, dy in offsets:
            surf = self._title_font.render(title, True, BLACK)
            surface.blit(surf, surf.get_rect(center=center).move(dx, dy))
        surf = self._title_font.render(title, True, WHITE)
        surface.blit(surf, surf.get_rect(center=center))

    def _draw_table(self, surface: pygame.Surface) -> None:
        table_left = int(WIDTH * _TABLE_LEFT_RATIO)
        table_right = int(WIDTH * _TABLE_RIGHT_RATIO)
        col_rank = int(WIDTH * _COL_RANK_X_RATIO)
        col_name = int(WIDTH * _COL_NAME_X_RATIO)
        col_time = int(WIDTH * _COL_TIME_X_RATIO)
        col_date = int(WIDTH * _COL_DATE_X_RATIO)
        header_y = 136

        self._draw_header_row(surface, header_y, col_rank, col_name, col_time, col_date)

        sep_y = header_y + 34
        pygame.draw.line(
            surface,
            BLACK,
            (table_left, sep_y),
            (table_right, sep_y),
            2,
        )

        if not self._records:
            self._draw_empty_message(surface)
            return

        row_h = 70
        for i, record in enumerate(self._records):
            y = sep_y + 10 + i * row_h
            self._draw_record_row(surface, record, i, y, col_rank, col_name, col_time, col_date, table_left, table_right)

    def _draw_header_row(
        self,
        surface: pygame.Surface,
        y: int,
        col_rank: int,
        col_name: int,
        col_time: int,
        col_date: int,
    ) -> None:
        headers = [
            ("RANK", col_rank),
            ("JOGADOR", col_name),
            ("TEMPO", col_time),
            ("DATA", col_date),
        ]
        for label, x in headers:
            surf = self._header_font.render(label, True, BLUE)
            surface.blit(surf, (x, y))

    def _draw_record_row(
        self,
        surface: pygame.Surface,
        record: dict,
        index: int,
        y: int,
        col_rank: int,
        col_name: int,
        col_time: int,
        col_date: int,
        table_left: int,
        table_right: int,
    ) -> None:
        row_rect = pygame.Rect(table_left, y, table_right - table_left, 62)

        if index == 0:
            pygame.draw.rect(surface, GREEN_LOCKED, row_rect, border_radius=10)
            pygame.draw.rect(surface, BLACK, row_rect, width=2, border_radius=10)
        elif index % 2 == 0:
            pygame.draw.rect(surface, (230, 240, 255), row_rect, border_radius=8)

        rank_label = f"#{index + 1}"
        name_label = str(record.get("name", "?"))[:20]
        time_val = record.get("time")
        time_label = self._format_time(float(time_val)) if time_val is not None else "—"
        date_label = str(record.get("date", ""))

        rank_color = ORANGE if index == 0 else BLACK
        mid_y = y + 18

        surface.blit(self._row_font.render(rank_label, True, rank_color), (col_rank, mid_y))
        surface.blit(self._row_font.render(name_label, True, BLACK), (col_name, mid_y))
        surface.blit(self._row_font.render(time_label, True, BLACK), (col_time, mid_y))
        surface.blit(self._row_font.render(date_label, True, BLACK), (col_date, mid_y))

    def _draw_empty_message(self, surface: pygame.Surface) -> None:
        msg = "Nenhum recorde ainda. Complete o torneio para aparecer aqui!"
        surf = self._empty_font.render(msg, True, BLACK)
        surface.blit(surf, surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

    def _format_time(self, seconds: float) -> str:
        """Formata segundos no padrao MM:SS.

        Args:
            seconds: Duracao em segundos.

        Returns:
            String no formato ``MM:SS``.
        """
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"

    def _draw_hint(self, surface: pygame.Surface) -> None:
        hint = "ENTER ou ESC para voltar ao menu"
        surf = self._hint_font.render(hint, True, BLACK)
        surface.blit(surf, surf.get_rect(center=(WIDTH // 2, HEIGHT - 32)))
