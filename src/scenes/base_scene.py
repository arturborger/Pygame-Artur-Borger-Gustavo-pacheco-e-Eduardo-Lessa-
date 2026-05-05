"""Classe base abstrata para cenas do jogo."""

from __future__ import annotations

import abc


class BaseScene(abc.ABC):
    """Define o contrato comum para todas as cenas do jogo.

    Args:
        game: Instancia principal do jogo, usada pela cena para acessar
            estado compartilhado e solicitar acoes globais.
    """

    def __init__(self, game) -> None:
        """Inicializa a cena com uma referencia para o jogo.

        Args:
            game: Instancia principal do jogo que criou ou controla a cena.
        """
        self.game = game

    @abc.abstractmethod
    def handle_events(self, events) -> None:
        """Processa os eventos recebidos pela cena.

        Args:
            events: Sequencia de eventos capturados no quadro atual.

        Returns:
            None. Implementacoes devem atualizar apenas o estado interno da
            cena ou solicitar acoes ao jogo.
        """

    @abc.abstractmethod
    def update(self, dt) -> None:
        """Atualiza o estado da cena.

        Args:
            dt: Tempo decorrido desde o ultimo quadro, em segundos.

        Returns:
            None. Implementacoes devem aplicar a logica da cena para o
            intervalo informado.
        """

    @abc.abstractmethod
    def draw(self, surface) -> None:
        """Desenha a cena na superficie informada.

        Args:
            surface: Superficie onde a cena deve renderizar seu conteudo.

        Returns:
            None. Implementacoes devem apenas desenhar na superficie recebida.
        """

    @abc.abstractmethod
    def next_scene(self) -> BaseScene | None:
        """Informa qual cena deve ser ativada apos a cena atual.

        Returns:
            Proxima cena a ser ativada, ou None quando a cena atual deve
            continuar ativa.
        """
