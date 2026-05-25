"""Leitura e escrita dos highscores do jogo em JSON."""

from __future__ import annotations

import json
import os
from datetime import date

from src.settings import HIGHSCORE_PATH


class HighscoreManager:
    """Gerencia rankings top 5 para torneio, 2P e treino."""

    _CATEGORIES = ("tournament", "2p", "training")
    _MAX_RECORDS = 5

    def __init__(self, path: str = HIGHSCORE_PATH) -> None:
        """Carrega highscores existentes ou inicializa listas vazias.

        Args:
            path: Caminho do arquivo JSON de highscores.
        """
        self.path = path
        self._data = self._load()

    def add_tournament_record(self, name: str, opponents_beaten: int) -> None:
        """Adiciona um resultado de torneio e salva o top 5.

        Args:
            name: Nome do jogador.
            opponents_beaten: Quantidade de adversarios vencidos no torneio.
        """
        self._add_record("tournament", name, "opponents", opponents_beaten)

    def add_tournament_time_record(self, name: str, time_seconds: float) -> None:
        """Adiciona um recorde de torneio concluido com o tempo total e salva o top 5.

        Apenas partidas concluidas (todos os adversarios vencidos) devem chamar
        este metodo. Registros com menor tempo ficam em posicoes superiores.

        Args:
            name: Nome do jogador conforme digitado na tela de entrada.
            time_seconds: Tempo total em segundos para completar o torneio.
        """
        self._validate_category("tournament")
        record = {
            "name": name,
            "time": round(float(time_seconds), 1),
            "date": date.today().isoformat(),
        }
        self._data["tournament"].append(record)
        self._trim_category("tournament", self._data)
        self.save()

    def add_2p_record(self, name: str, opponents_beaten: int) -> None:
        """Adiciona um resultado do modo 2P e salva o top 5.

        Args:
            name: Nome do jogador ou dupla vencedora.
            opponents_beaten: Quantidade usada para ordenar o ranking do modo 2P.
        """
        self._add_record("2p", name, "opponents", opponents_beaten)

    def add_training_record(self, name: str, maior_rally: int) -> None:
        """Adiciona um resultado de treino e salva o top 5.

        Args:
            name: Nome do jogador.
            maior_rally: Maior rally obtido no modo treino.
        """
        self._add_record("training", name, "maior_rally", maior_rally)

    def get_top(self, category: str) -> list[dict[str, int | str]]:
        """Retorna uma copia do ranking da categoria solicitada.

        Args:
            category: Uma das categorias ``"tournament"``, ``"2p"`` ou
                ``"training"``.

        Returns:
            Lista de registros ja ordenados do melhor para o pior.

        Raises:
            ValueError: Se a categoria informada for invalida.
        """
        self._validate_category(category)
        return [record.copy() for record in self._data[category]]

    def save(self) -> None:
        """Escreve os highscores em JSON indentado no caminho configurado."""
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        try:
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(self._data, file, indent=2, ensure_ascii=False)
        except OSError:
            return

    def _load(self) -> dict[str, list[dict[str, int | str]]]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                loaded = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return self._empty_data()

        if not isinstance(loaded, dict):
            return self._empty_data()

        data = self._empty_data()
        for category in self._CATEGORIES:
            records = loaded.get(category, [])
            if isinstance(records, list):
                data[category] = [
                    record.copy() for record in records if isinstance(record, dict)
                ]
                self._trim_category(category, data)

        return data

    def _add_record(
        self,
        category: str,
        name: str,
        score_key: str,
        score_value: int,
    ) -> None:
        self._validate_category(category)
        record = {
            "name": name,
            score_key: int(score_value),
            "date": date.today().isoformat(),
        }
        self._data[category].append(record)
        self._trim_category(category, self._data)
        self.save()

    def _trim_category(
        self,
        category: str,
        data: dict[str, list[dict[str, int | str]]],
    ) -> None:
        if category == "tournament":
            # Registros com campo "time" ordenados por tempo crescente (menor = melhor).
            # Registros antigos sem "time" (apenas "opponents") vao para o final.
            def _tournament_key(record: dict) -> tuple:
                time_val = record.get("time")
                if time_val is not None:
                    try:
                        return (0, float(time_val))
                    except (TypeError, ValueError):
                        pass
                return (1, 0.0)

            data[category].sort(key=_tournament_key)
        elif category == "training":
            data[category].sort(
                key=lambda record: self._score_value(record, "maior_rally"),
                reverse=True,
            )
        else:
            data[category].sort(
                key=lambda record: self._score_value(record, "opponents"),
                reverse=True,
            )
        data[category] = data[category][: self._MAX_RECORDS]

    def _score_value(self, record: dict[str, int | str], score_key: str) -> int:
        value = record.get(score_key, 0)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return 0

    def _empty_data(self) -> dict[str, list[dict[str, int | str]]]:
        return {category: [] for category in self._CATEGORIES}

    def _validate_category(self, category: str) -> None:
        if category not in self._CATEGORIES:
            raise ValueError(
                "Categoria invalida: "
                f"{category!r}. Use 'tournament', '2p' ou 'training'."
            )
