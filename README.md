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

## src/settings.py
- Sub-tarefa: A.1
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (constantes vieram do plano).

## src/game.py e main.py
- Sub-tarefa: A.2
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (foi criada a classe `Game` com loop principal,
  gerenciamento de cenas por `change_scene`, atributos base do jogo e uma cena
  placeholder; `main.py` apenas instancia `Game` e chama `run()`).

## src/scenes/base_scene.py
- Sub-tarefa: A.3
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (foi criada a classe abstrata `BaseScene` com
  construtor recebendo `game`, métodos abstratos para eventos, atualização,
  desenho e transição de cena, além de docstrings Google em português).

## src/assets_generator.py
- Sub-tarefa: B.1
- Dev integrador: Eduardo Lessa
- Ajustes manuais: paleta de cores ajustada para melhor contraste; foram
  criadas as funcoes `make_court`, `make_player_sprite` e `make_ai_sprite`
  usando apenas `pygame.draw`, com sombras simples e contornos pretos.

## src/assets_generator.py
- Sub-tarefa: B.2
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (foram criadas as funcoes `make_ball`,
  `make_trophy` e `make_button`, usando apenas `pygame.draw`, superficies com
  `SRCALPHA`, contornos pretos e texto centralizado em fonte default negrito).

Toda a equipe revisou criticamente o código gerado, validou seu funcionamento e é
capaz de explicar cada trecho. Bugs introduzidos pela IA foram corrigidos pela equipe,
conforme orientação do curso.

## src/assets_generator.py, src/utils/asset_cache.py e src/game.py
- Sub-tarefa: B.3
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (foi criada a funcao
  `make_swing_animation_frames`, com 4 superficies de animacao de rebatida;
  tambem foi criada a classe `AssetCache` para reutilizar assets sob demanda,
  e `Game` passou a instanciar um unico cache em `self.assets`).

## src/entities/ball.py
- Sub-tarefa: C.1
- Dev integrador: Arthur Borger
- Ajustes manuais: nenhum (foi criada a classe `Ball` herdando de
  `pygame.sprite.Sprite`, com imagem vinda do `AssetCache` via `make_ball`,
  `rect`, `mask`, posição e velocidade em `Vector2`, controle de último
  rebatedor, contagem de quicadas, atualização por `dt` e reset para o lado
  sacador).

## src/entities/ball.py
- Sub-tarefa: C.2
- Dev integrador: Arthur Borger
- Ajustes manuais: nenhum (foi adicionado o método `apply_shot`, que calcula
  `final_angle`, `final_speed`, `direction_y` e o novo vetor `velocity` com
  `Vector2`, aplicando jitter quando a força fica fora do sweet spot e
  retornando `True` quando a rebatida é aplicada).

## src/systems/physics.py
- Sub-tarefa: C.3
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (foram criadas funções puras para refletir a bola nas
  bordas laterais com `bounce_off_walls`, detectar saída pelo topo ou fundo com
  `is_out_of_bounds` e identificar contato com a rede usando `hit_net`).

## src/systems/timing_bars.py
- Sub-tarefa: D.1
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (foi criada a classe `TimingBars` com estados
  `IDLE`, `AIMING`, `POWERING` e `LOCKED`, ativação da barra de ângulo,
  oscilação entre `AIM_MIN_ANGLE` e `AIM_MAX_ANGLE`, reset, consulta de estado
  ativo e stubs documentados para as próximas etapas).

## src/systems/timing_bars.py
- Sub-tarefa: D.2
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (a classe `TimingBars` passou a oscilar a barra de
  força em `POWERING`, travar ângulo e força em sequência com
  `handle_lock_press`, guardar o tempo de congelamento em `frozen_until`,
  expor `get_locked_values`, identificar `LOCKED` em `is_locked` e detectar o
  sweet spot pela faixa configurada em `settings.py`).

## src/systems/timing_bars.py e src/settings.py
- Sub-tarefa: D.3
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (foi implementado `TimingBars.draw` com barras
  cartoon de ângulo e força, contorno escuro, cantos arredondados, zona verde
  de sweet spot, cursores por estado e marca fixa do ângulo travado; os
  parâmetros visuais novos ficaram centralizados em `src/settings.py`).
