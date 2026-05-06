"""Gerenciamento de sons sinteticos do jogo."""

from __future__ import annotations

import pygame


class SoundManager:
    """Cria e toca efeitos sonoros gerados em tempo de execucao."""

    def __init__(self) -> None:
        """Inicializa o mixer e prepara os sons base do jogo."""
        self.enabled = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._np = None
        self.frequency = 44100
        self.channels = 1

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.frequency, size=-16, channels=1)
            self.frequency, _, self.channels = pygame.mixer.get_init()
            import numpy as np
        except (ImportError, pygame.error):
            return

        self._np = np
        self.enabled = True
        try:
            self._build_base_sounds()
        except pygame.error:
            self.enabled = False
            self._sounds.clear()

    def play(self, name: str) -> None:
        """Toca um som pelo nome, ignorando nomes ausentes ou audio indisponivel."""
        if not self.enabled:
            return

        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def _build_base_sounds(self) -> None:
        self._sounds["hit"] = self._tone(600, 0.08, 0.55)
        self._sounds["bounce"] = self._tone(300, 0.06, 0.42)
        self._sounds["score"] = self._sequence((293.66, 392.00), 0.15, 0.45)
        self._sounds["ace"] = self._sequence((523.25, 659.25, 783.99), 0.10, 0.50)
        self._sounds["menu_click"] = self._menu_click()

    def _tone(self, frequency: float, duration: float, volume: float) -> pygame.mixer.Sound:
        return self._make_sound(self._tone_wave(frequency, duration, volume))

    def _sequence(
        self,
        frequencies: tuple[float, ...],
        note_duration: float,
        volume: float,
    ) -> pygame.mixer.Sound:
        np = self._np
        waves = [
            self._tone_wave(frequency, note_duration, volume)
            for frequency in frequencies
        ]
        return self._make_sound(np.concatenate(waves))

    def _menu_click(self) -> pygame.mixer.Sound:
        np = self._np
        sample_count = max(1, int(self.frequency * 0.05))
        noise = np.random.default_rng().uniform(-1.0, 1.0, sample_count)
        kernel = np.ones(8) / 8
        filtered = np.convolve(noise, kernel, mode="same")
        envelope = np.linspace(1.0, 0.0, sample_count)
        return self._make_sound(filtered * envelope * 0.35)

    def _tone_wave(self, frequency: float, duration: float, volume: float):
        np = self._np
        sample_count = max(1, int(self.frequency * duration))
        times = np.linspace(0, duration, sample_count, endpoint=False)
        envelope = np.linspace(1.0, 0.0, sample_count)
        return np.sin(2 * np.pi * frequency * times) * envelope * volume

    def _make_sound(self, wave) -> pygame.mixer.Sound:
        np = self._np
        samples = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        if self.channels > 1:
            samples = np.repeat(samples[:, None], self.channels, axis=1)
        return pygame.sndarray.make_sound(samples)
