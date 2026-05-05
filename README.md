# 🎾 Tennis Cartoon — Projeto Final DesSoft

Jogo de tênis 2D top-down em estilo cartoon, com **mecânica única de mini-game de
timing sequencial** (trave o ângulo, depois a força!) e **pontuação oficial do tênis**
(15-30-40-deuce-advantage-tiebreak, melhor de 3 sets).

## Integrantes

- Arthur Borger
- Eduardo Lessa
- Gustavo Pacheco

## Modos de Jogo

- 🏆 Torneio (1P vs CPU): vença 3 adversários progressivos em praia, floresta e estádio
- 👥 2 Jogadores Local (mesmo teclado)
- 🎯 Modo Treino (parede ou bot rebatedor)

## Como rodar

```bash
git clone <url>
pip install -r requirements.txt
python main.py
```

## Vídeo de demonstração

🔗 [link do YouTube]

## Controles

| Ação | P1 | P2 |
|------|----|----|
| Mover | Setas | W A S D |
| Travar barras (ângulo, depois força) | ESPAÇO | SHIFT direito |
| Pause | P / ESC | - |

## Como funciona a mecânica

1. Quando a bola se aproxima, a **BARRA DE ÂNGULO** oscila — pressione ESPAÇO para travar.
2. Depois a **BARRA DE FORÇA** oscila com uma zona verde (sweet spot 70-90%) — pressione ESPAÇO de novo.
3. Acertar no sweet spot evita erros de mira e marca um winner.

## Pontuação

Sistema oficial do tênis: 0 → 15 → 30 → 40 → game · 6 games = set (com 2 de vantagem) ·
tie-break a 7 quando 6-6 · melhor de 3 sets vence a partida.

## Estatísticas

Ao fim de cada partida você vê: aces e winners de cada jogador.

## Assets

**Todos os gráficos foram gerados em código Python via `pygame.draw`** (formas geométricas
cartoon coloridas) — nenhum sprite externo foi usado. Veja `src/assets_generator.py`.
Os sons também são sintetizados em runtime via numpy + pygame.sndarray.

## Dependências

- Python 3.10+
- pygame >= 2.5
- numpy >= 1.20

## Uso de Inteligência Artificial Generativa

Este projeto foi planejado com auxílio de uma LLM que produziu o documento
`plano_jogo_tenis_codex.md` com a divisão de tarefas, e cada sub-tarefa foi enviada
como prompt para o Codex (ChatGPT). Esta seção registra, tarefa por tarefa, como a IA
foi usada no desenvolvimento. O detalhamento por arquivo também pode ser mantido em
`docs/ai_usage.md`.

### Registro por tarefa

| Tarefa | Descrição | Arquivos principais | Histórico do chat | Revisão humana / ajustes |
|--------|-----------|---------------------|-------------------|--------------------------|
| A.1 | Estrutura de pastas e `settings.py` | `src/settings.py`, `__init__.py`, `requirements.txt`, `.gitignore`, `README.md` | [link do histórico deste chat](<INSERIR_LINK_DO_HISTORICO_DO_CHAT>) | Constantes conferidas com as seções 4 e 5; `settings.py` validado com parse de sintaxe. |
| A.2 | `main.py` e classe `Game` | A preencher | A preencher | A preencher |
| A.3 | `BaseScene` abstrata | A preencher | A preencher | A preencher |
| B.1 | Sprites de quadra e personagens | A preencher | A preencher | A preencher |
| B.2 | Sprites de bola, troféu e UI | A preencher | A preencher | A preencher |
| B.3 | Animação de rebatida e cache de assets | A preencher | A preencher | A preencher |
| C.1 | Classe `Ball` básica | A preencher | A preencher | A preencher |
| C.2 | Aplicação de rebatida | A preencher | A preencher | A preencher |
| C.3 | Detecção de bordas e rede | A preencher | A preencher | A preencher |
| D.1 | Estado `AIMING` da barra de ângulo | A preencher | A preencher | A preencher |
| D.2 | Estado `POWERING` e travamento sequencial | A preencher | A preencher | A preencher |
| D.3 | Renderização cartoon das barras | A preencher | A preencher | A preencher |
| E.1 | Classe `Player` com movimento | A preencher | A preencher | A preencher |
| E.2 | Integração `Player` com `TimingBars` e `try_hit` | A preencher | A preencher | A preencher |
| E.3 | Classe `AIPlayer` | A preencher | A preencher | A preencher |
| F.1 | Lógica de game | A preencher | A preencher | A preencher |
| F.2 | Lógica de set e tie-break | A preencher | A preencher | A preencher |
| F.3 | Match, alternância de saque e interface completa | A preencher | A preencher | A preencher |
| G.1 | Colisão jogador-bola com máscara | A preencher | A preencher | A preencher |
| G.2 | `StatsTracker` | A preencher | A preencher | A preencher |
| G.3 | `HighscoreManager` | A preencher | A preencher | A preencher |
| H.1 | `MenuScene` | A preencher | A preencher | A preencher |
| H.2 | `InstructionsScene` | A preencher | A preencher | A preencher |
| H.3 | `TournamentScene` | A preencher | A preencher | A preencher |
| I.1 | Setup da `GameplayScene` | A preencher | A preencher | A preencher |
| I.2 | Lógica de pontuação no gameplay | A preencher | A preencher | A preencher |
| I.3 | HUD da gameplay | A preencher | A preencher | A preencher |
| J.1 | `PauseScene` | A preencher | A preencher | A preencher |
| J.2 | `StatsScene` | A preencher | A preencher | A preencher |
| J.3 | `GameOverScene` e integração com highscore | A preencher | A preencher | A preencher |
| K.1 | `SoundManager` e sons de hit/bounce | A preencher | A preencher | A preencher |
| K.2 | Sons de score/ace/menu | A preencher | A preencher | A preencher |
| K.3 | Música ambiente sintética | A preencher | A preencher | A preencher |
| L.1 | Modo 2 jogadores | A preencher | A preencher | A preencher |
| L.2 | `PracticeBot` e modo treino | A preencher | A preencher | A preencher |
| L.3 | Modo parede e persistência de rally | A preencher | A preencher | A preencher |

### Modelo para novas entradas

Ao concluir uma tarefa, substitua os campos `A preencher` por:

- arquivos criados ou alterados;
- link público ou compartilhável do histórico do chat usado na tarefa;
- resumo da revisão humana feita pela equipe e ajustes manuais aplicados.

Toda a equipe revisou criticamente o código gerado, validou seu funcionamento e é
capaz de explicar cada trecho. Bugs introduzidos pela IA foram corrigidos pela equipe,
conforme orientação do curso.
