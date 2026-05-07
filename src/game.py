"""Loop principal e gerenciamento de cenas do jogo."""

from __future__ import annotations

import pygame

from src.scenes.menu_scene import MenuScene
from src.settings import FPS, HEIGHT, TITLE, WIDTH
from src.systems.highscore import HighscoreManager
from src.utils.asset_cache import AssetCache
from src.utils.sound_manager import SoundManager


class Game:
    """Controla a janela, o loop principal e a cena ativa do jogo.

    Attributes:
        screen: Superfície principal criada pelo Pygame.
        clock: Relógio usado para limitar o FPS e calcular o delta time.
        running: Indica se o loop principal deve continuar executando.
        scene: Cena ativa do jogo.
        assets: Cache unico para assets gerados ou carregados sob demanda.
        sound_manager: Gerenciador de sons, ainda não implementado.
    """

    def __init__(self) -> None:
        """Inicializa o Pygame, a janela, o relógio e a cena inicial."""
        pygame.init()
        info = pygame.display.Info()
        scale = min(info.current_w / WIDTH, info.current_h / HEIGHT, 1.0)
        self._win_w = int(WIDTH * scale)
        self._win_h = int(HEIGHT * scale)
        self._window = pygame.display.set_mode((self._win_w, self._win_h))
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.assets = AssetCache()
        self.sound_manager = SoundManager()
        self.highscore_manager = HighscoreManager()
        self.tournament_progress = 0
        self.scene = MenuScene(self)

    def change_scene(self, scene: object) -> None:
        """Troca a cena ativa do jogo.

        Args:
            scene: Nova cena. Deve implementar `handle_events`, `update` e `draw`.
        """
        self.scene = scene

    def run(self) -> None:
        """Executa o loop principal do jogo até o encerramento."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene.handle_events(events)
            self.scene.update(dt)
            next_scene = self.scene.next_scene()
            if next_scene is not None:
                self.change_scene(next_scene)

            self.scene.draw(self.screen)
            scaled = pygame.transform.scale(self.screen, (self._win_w, self._win_h))
            self._window.blit(scaled, (0, 0))
            pygame.display.flip()

        self.sound_manager.stop_music()
        pygame.quit()
