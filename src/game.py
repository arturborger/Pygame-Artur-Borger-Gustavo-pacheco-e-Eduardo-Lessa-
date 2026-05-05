"""Loop principal e gerenciamento de cenas do jogo."""

from __future__ import annotations

import pygame

from src.settings import FPS, GREEN_SWEET, HEIGHT, TITLE, WIDTH


class PlaceholderScene:
    """Cena inicial temporária usada enquanto as cenas reais não existem."""

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa eventos da cena.

        Args:
            events: Lista de eventos capturados pelo Pygame neste quadro.
        """

    def update(self, dt: float) -> None:
        """Atualiza o estado da cena.

        Args:
            dt: Tempo decorrido desde o último quadro, em segundos.
        """

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha a cena na tela.

        Args:
            screen: Superfície principal onde a cena deve ser desenhada.
        """
        screen.fill(GREEN_SWEET)


class Game:
    """Controla a janela, o loop principal e a cena ativa do jogo.

    Attributes:
        screen: Superfície principal criada pelo Pygame.
        clock: Relógio usado para limitar o FPS e calcular o delta time.
        running: Indica se o loop principal deve continuar executando.
        scene: Cena ativa do jogo.
        assets: Dicionário placeholder para assets carregados futuramente.
        sound_manager: Gerenciador de sons, ainda não implementado.
    """

    def __init__(self) -> None:
        """Inicializa o Pygame, a janela, o relógio e a cena inicial."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = PlaceholderScene()
        self.assets = {}
        self.sound_manager = None

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
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
