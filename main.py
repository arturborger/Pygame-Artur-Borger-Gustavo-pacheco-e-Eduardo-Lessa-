"""Ponto de entrada do jogo de tênis cartoon."""

from src.game import Game


def main() -> None:
    """Instancia o jogo e inicia o loop principal."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
