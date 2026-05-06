# 🎾 Tennis Cartoon — Projeto Final DesSoft

Jogo de tênis 2D top-down em estilo cartoon, com **mecânica única de mini-game de
timing sequencial** (trave o ângulo, depois a força!) e **pontuação oficial do tênis**
(15-30-40-deuce-advantage-tiebreak, melhor de 3 sets).

## Integrantes

- Artur Borger
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

As partidas usam a quadra na horizontal: o P1 joga pela esquerda e o P2/CPU
joga pela direita.

1. Quando a bola bate no jogador humano, ela para ao lado dele e abre a **BARRA DE ÂNGULO**.
2. Pressione ESPAÇO para travar o ângulo; depois a **BARRA DE FORÇA** oscila com uma zona verde (sweet spot 70-90%).
3. Uma flecha mostra a direção prevista da bola e muda de tamanho conforme a força selecionada.
4. Pressione ESPAÇO de novo para travar a força e soltar a bola a partir do jogador.
5. Acertar no sweet spot evita erros de mira e marca um winner.

## Pontuação

Sistema oficial do tênis: 0 → 15 → 30 → 40 → game · 6 games = set (com 2 de vantagem) ·
tie-break a 7 quando 6-6 · melhor de 3 sets vence a partida.

## Estatísticas

Ao fim de cada partida você vê: aces e winners de cada jogador. Essas métricas
ficam disponíveis por uma fachada simples (`StatsTracker`) para a UI consultar
sem depender da lógica completa do placar.

## Highscores

O jogo salva rankings top 5 em `data/highscores.json` para torneio, 2 jogadores
local e treino. Se o arquivo não existir ou estiver inválido, o ranking começa
vazio e é recriado automaticamente ao salvar um novo resultado.

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
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi criada a classe `Ball` herdando de
  `pygame.sprite.Sprite`, com imagem vinda do `AssetCache` via `make_ball`,
  `rect`, `mask`, posição e velocidade em `Vector2`, controle de último
  rebatedor, contagem de quicadas, atualização por `dt` e reset para o lado
  sacador).

## src/entities/ball.py
- Sub-tarefa: C.2
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi adicionado o método `apply_shot`, que calcula
  `final_angle`, `final_speed`, `direction_x` e o novo vetor `velocity` com
  `Vector2`, aplicando jitter quando a força fica fora do sweet spot e
  retornando `True` quando a rebatida é aplicada).

## src/systems/physics.py
- Sub-tarefa: C.3
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (foram criadas funções puras para refletir a bola nas
  bordas horizontais com `bounce_off_walls`, detectar saída pela esquerda ou
  direita com `is_out_of_bounds` e identificar contato com a rede usando
  `hit_net`).

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

## src/entities/player.py
- Sub-tarefa: E.1
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (foi criada a classe `Player` herdando de
  `pygame.sprite.Sprite`, com sprite vindo do `AssetCache`, controles
  configuraveis, posicao inicial por lado da quadra, movimento por `dt`,
  restricao ao proprio campo e instancia de `TimingBars`).

## src/entities/player.py
- Sub-tarefa: E.2
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (a classe `Player` passou a processar a tecla de
  trava com `handle_event`, ativar `TimingBars` automaticamente quando a bola
  se aproxima na direcao correta, verificar `can_hit` por distancia ate
  `HIT_RADIUS` e aplicar rebatidas em `try_hit` usando os valores travados).

## src/entities/ai_player.py
- Sub-tarefa: E.3
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (foi criada a classe `AIPlayer` herdando de `Player`,
  sem entrada de teclado, com sprite do adversario, `reaction_timer`, `target_y`,
  movimento limitado por `max_speed`, erro de mira por dificuldade e rebatida
  direta com angulo e forca sorteados).

## src/systems/score_manager.py
- Sub-tarefa: F.1
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (foi criada a classe `ScoreManager` com placar de
  game no formato 0-15-30-40, regras de deuce e advantage, incremento de games
  ao fechar pontos com dois de vantagem e estatísticas simples de aces e
  winners).

## src/systems/score_manager.py
- Sub-tarefa: F.2
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (o `ScoreManager` passou a fechar sets em 6 games
  com dois de vantagem, entrar em tie-break no 6-6, pontuar tie-break de forma
  numérica até 7 com dois de vantagem e registrar o histórico de sets).

## src/systems/score_manager.py
- Sub-tarefa: F.3
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: nenhum (o `ScoreManager` foi finalizado com match melhor
  de 3 sets, vencedor da partida, interface pública completa e alternância de
  saque por game e por pontos no tie-break).

## src/systems/collision.py
- Sub-tarefa: G.1
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi criada a função `player_hits_ball`, usando
  `pygame.sprite.collide_mask` com cooldown em milissegundos para evitar
  múltiplas detecções da mesma colisão; `check_ball_out_of_bounds` delega para
  `physics.is_out_of_bounds`).

## src/systems/stats_tracker.py
- Sub-tarefa: G.2
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi criada a classe `StatsTracker` com contadores de
  aces e winners para `p1` e `p2`, métodos `register_ace`,
  `register_winner`, `get` e `reset`, servindo como fachada simples para a UI).

## src/systems/highscore.py
- Sub-tarefa: G.3
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi criada a classe `HighscoreManager`, com carga
  resiliente de JSON, categorias `tournament`, `2p` e `training`, salvamento
  indentado, data ISO e manutenção automática do top 5 por categoria).

## src/scenes/menu_scene.py e src/game.py
- Sub-tarefa: H.1
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi criada a `MenuScene` cartoon com seis opcoes,
  navegacao por setas, ENTER para acionar e ESC para sair; `Game` passou a
  iniciar pelo menu, manter `tournament_progress` e consultar `next_scene()` a
  cada quadro para permitir transicoes entre cenas).

## src/scenes/instructions_scene.py
- Sub-tarefa: H.2
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi criada a `InstructionsScene`, com controles,
  explicacao da mecanica sequencial de angulo e forca, frase de pontuacao,
  retorno ao menu por ENTER/ESC e demonstracao visual das duas barras com
  cursores ilustrativos).

## src/scenes/tournament_scene.py
- Sub-tarefa: H.3
- Dev integrador: Artur Borger
- Ajustes manuais: nenhum (foi criada a `TournamentScene`, lendo
  `game.tournament_progress`, desenhando tres cards horizontais dos adversarios
  do torneio, estados vencido/proximo/bloqueado, painel de detalhes por setas,
  trofeu ao completar as tres fases e tentativa preparada de abrir
  `GameplayScene(mode="1p", opponent_id=...)` quando ela existir).

## src/entities/player.py, src/systems/timing_bars.py, src/settings.py e src/scenes/gameplay_scene.py
- Sub-tarefa: Polimento de mira
- Dev integrador: Artur Borger
- Ajustes manuais: foi adicionada uma flecha de trajetoria durante a selecao
  de angulo e forca; ela usa o mesmo vetor da rebatida, nasce perto da bola,
  aumenta e diminui junto com a forca atual e respeita os modos 1P, 2P e
  treino da `GameplayScene`.

## src/scenes/gameplay_scene.py e src/settings.py
- Sub-tarefa: I.1
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: foram centralizados `CONTROLS_P1` e `CONTROLS_P2` em
  `src/settings.py`; a `GameplayScene` foi criada integrando quadra, jogador,
  IA, bola, `ScoreManager`, `StatsTracker`, atualização básica, colisão com
  cooldown e desenho das entidades e barras de timing.

## src/scenes/gameplay_scene.py e src/entities/ball.py
- Sub-tarefa: I.2
- Dev integrador: Gustavo pacheco
- Ajustes manuais: a cena passou a detectar bola fora pela esquerda/direita,
  converter lados `left/right` para `p1/p2`, registrar pontos no
  `ScoreManager`, atualizar `StatsTracker` para aces e winners, reiniciar o
  ponto a partir do sacador atual e preparar a transicao para `StatsScene` ao
  fim da partida; `Ball` recebeu estado explicito de saque e qualidade da
  ultima rebatida para classificar o ponto.

## src/scenes/gameplay_scene.py
- Sub-tarefa: I.3
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: foi adicionado `draw_hud`, com painel semi-transparente,
  nomes dos jogadores, placar 15-30-40/AD, games do set, bolinhas de sets
  vencidos, indicador visual de saque e selo de tie-break.

## src/scenes/pause_scene.py e src/scenes/gameplay_scene.py
- Sub-tarefa: J.1
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: foi criada a `PauseScene` como overlay, desenhando a
  gameplay congelada por tras, painel central com `CONTINUAR` e
  `MENU PRINCIPAL`, navegacao por setas/ENTER e retorno por ESC/P; a
  `GameplayScene` passou a abrir a pausa com ESC ou P.

## src/scenes/stats_scene.py e src/scenes/gameplay_scene.py
- Sub-tarefa: J.2
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: foi criada a `StatsScene`, exibindo estatisticas finais em
  duas colunas com nome, sets vencidos, aces, winners e historico de sets; a
  `GameplayScene` passou a repassar o modo de jogo para a tela de estatisticas.

## src/scenes/game_over_scene.py e src/game.py
- Sub-tarefa: J.3
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: foi criada a `GameOverScene`, com texto de vitoria/derrota,
  trofeu animado quando o jogador vence no torneio, retorno ao torneio ou menu
  por ENTER, incremento de `game.tournament_progress` e salvamento de recordes
  via `HighscoreManager`, agora instanciado em `Game`.

## src/utils/sound_manager.py, src/game.py, src/scenes/gameplay_scene.py e requirements.txt
- Sub-tarefa: K.1
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (foi criada a classe `SoundManager`, com
  inicializacao resiliente do `pygame.mixer`, fallback silencioso quando audio
  ou numpy nao estiverem disponiveis, geracao runtime dos sons `hit` e
  `bounce` via `numpy` + `pygame.sndarray.make_sound`, integracao em `Game`,
  chamadas de `hit`/`bounce` na gameplay e inclusao de `numpy>=1.20` nas
  dependencias).

## src/utils/sound_manager.py, src/scenes/gameplay_scene.py e src/scenes/menu_scene.py
- Sub-tarefa: K.2
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (foram adicionados os sons sinteticos `score`,
  `ace` e `menu_click`, com sequencias tonais para pontuacao/ace, ruido branco
  curto filtrado por media movel para o menu, e chamadas na gameplay e no menu).

## src/utils/sound_manager.py, src/scenes/gameplay_scene.py, src/scenes/pause_scene.py e src/game.py
- Sub-tarefa: K.3
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (o `SoundManager` passou a gerar loops sinteticos
  por cenario em `play_music`, parar a trilha com `stop_music`, iniciar a
  musica ambiente na `GameplayScene` e interrompe-la ao fim da partida, ao
  voltar ao menu pela pausa e ao encerrar o jogo).

## src/scenes/gameplay_scene.py, src/scenes/menu_scene.py e src/scenes/game_over_scene.py
- Sub-tarefa: L.1
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (o modo `2p` passou a criar `Player 1` e
  `Player 2` humanos com controles independentes no mesmo teclado, reutilizando
  barras de timing e HUD por nomes configuraveis; o menu agora abre
  `GameplayScene(mode="2p")` e a tela final trata 2P como partida local com
  vencedor registrado).

## src/entities/practice_bot.py, src/scenes/gameplay_scene.py e src/scenes/menu_scene.py
- Sub-tarefa: L.2
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (foi criado o `PracticeBot`, que persegue a bola e
  rebate automaticamente no modo treino; `GameplayScene(mode="training")`
  desativa o placar oficial, usa `rally_count`, mostra HUD de rally e o menu
  passa a abrir o Modo Treino).

## src/scenes/gameplay_scene.py
- Sub-tarefa: L.3
- Dev integrador: Eduardo Lessa
- Ajustes manuais: nenhum (o modo treino passou a alternar com TAB entre bot
  e parede; no submodo parede a borda direita reflete a bola, `player2` fica
  ausente, o maior rally e salvo em highscore quando a bola sai e a HUD mostra
  `RECORDE: N`).

## Ajuste posterior de orientação horizontal
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: as quadras geradas por `make_court`, os previews do menu e
  da tela final, a física da bola, os lados dos jogadores, a IA e o modo treino
  foram convertidos para orientação horizontal, com P1 à esquerda e P2/CPU à
  direita.

## src/entities/ball.py, src/entities/player.py e src/scenes/gameplay_scene.py
- Sub-tarefa: Ajuste de rebatida com bola parada no jogador
- Dev integrador: Gustavo Pacheco
- Ajustes manuais: a bola passou a zerar a velocidade e ficar presa ao jogador
  humano quando colide com ele; as barras sequenciais agora são ativadas nesse
  contato, travam ângulo e força em ordem e liberam a bola imediatamente após a
  seleção da força.
