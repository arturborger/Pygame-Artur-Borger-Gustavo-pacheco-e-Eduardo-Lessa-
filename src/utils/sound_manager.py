"""Gerenciamento de sons sinteticos do jogo."""

from __future__ import annotations

import pygame


class SoundManager:
    """Cria e toca efeitos sonoros gerados em tempo de execucao."""

    def __init__(self) -> None:
        """Inicializa o mixer e prepara os sons base do jogo."""
        self.enabled = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._music_loops: dict[str, pygame.mixer.Sound] = {}
        self._music_channel: pygame.mixer.Channel | None = None
        self._current_music_id: str | None = None
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

    def play_music(self, scenery_id: str) -> None:
        """Toca em loop a musica sintetica do cenario informado."""
        if not self.enabled:
            return

        if (
            self._current_music_id == scenery_id
            and self._music_channel is not None
            and self._music_channel.get_busy()
        ):
            return

        self.stop_music()
        sound = self._music_loops.get(scenery_id)
        if sound is None:
            try:
                sound = self._build_music_loop(scenery_id)
            except pygame.error:
                return
            self._music_loops[scenery_id] = sound

        self._music_channel = sound.play(-1, 0, 400)
        self._current_music_id = scenery_id

    def stop_music(self) -> None:
        """Interrompe a musica ambiente atual, se houver."""
        if self._music_channel is not None:
            self._music_channel.stop()
        self._music_channel = None
        self._current_music_id = None

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

    def _build_music_loop(self, scenery_id: str) -> pygame.mixer.Sound:
        if scenery_id == "forest":
            notes = (196.00, 246.94, 220.00, 174.61, 196.00, 261.63, 246.94, 220.00)
            return self._make_sound(self._melody_wave(notes, 0.70, 0.25, "marimba"))

        if scenery_id == "stadium":
            notes = (130.81, None, 196.00, 196.00, 146.83, None, 220.00, 196.00)
            return self._make_sound(self._melody_wave(notes, 0.55, 0.30, "stadium"))

        notes = (392.00, 493.88, 587.33, 493.88, 440.00, 523.25, 659.25, 523.25)
        return self._make_sound(self._melody_wave(notes, 0.60, 0.24, "beach"))

    def _melody_wave(
        self,
        notes: tuple[float | None, ...],
        note_duration: float,
        volume: float,
        style: str,
    ):
        np = self._np
        waves = [
            self._rest_wave(note_duration)
            if frequency is None
            else self._instrument_wave(frequency, note_duration, volume, style)
            for frequency in notes
        ]
        return np.concatenate(waves)

    def _instrument_wave(
        self,
        frequency: float,
        duration: float,
        volume: float,
        style: str,
    ):
        np = self._np
        sample_count = max(1, int(self.frequency * duration))
        times = np.linspace(0, duration, sample_count, endpoint=False)

        if style == "beach":
            envelope = np.exp(-4.2 * times)
            wave = (
                np.sin(2 * np.pi * frequency * times)
                + 0.35 * np.sin(2 * np.pi * frequency * 2 * times)
            )
        elif style == "forest":
            envelope = np.exp(-5.8 * times)
            wave = (
                np.sin(2 * np.pi * frequency * times)
                + 0.22 * np.sin(2 * np.pi * frequency * 3 * times)
            )
        else:
            envelope = np.linspace(1.0, 0.0, sample_count) ** 2
            pulse = (np.sin(2 * np.pi * 7 * times) > -0.2).astype(float)
            wave = np.sin(2 * np.pi * frequency * times) * pulse

        return wave * envelope * volume

    def _rest_wave(self, duration: float):
        np = self._np
        return np.zeros(max(1, int(self.frequency * duration)))

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
