# Plano de Desenvolvimento — Jogo de Tênis 2D Cartoon (Projeto Final DesSoft)

> **Documento de referência para o Codex e para a equipe.**
> Toda implementação **DEVE** seguir as convenções, arquitetura e divisão descritas aqui.
> Critério de sucesso: gabaritar a rubrica do projeto final (conceito A em todos os 3 objetivos).

---

## 0. Resumo Executivo

Jogo de **tênis 2D top-down cartoon colorido** inspirado em Pong, com mecânica única
de **duas barras oscilantes sequenciais**: ao receber a bola, o jogador trava primeiro
a **barra de ângulo** com ESPAÇO, depois a **barra de força** também com ESPAÇO.

Pontuação no **sistema oficial do tênis** (15-30-40-game-set), modo principal em
**torneio progressivo** com 3 fases, e **assets gerados via código Python** (formas
geométricas com `pygame.draw`), com exceção do sprite do Rafael Nadal em PNG.

**Stack:** Python 3.10+, PyGame, Git/GitHub.
**Equipe:** 3 desenvolvedores (cada componente é dividido em 3 micro-tarefas).
**Entrega:** proposta 08/05/2026 · final 25/05/2026.

---

## 1. Decisões de Design (CONFIRMADAS — usar exatamente isto)

| Item | Decisão |
|------|---------|
| Perspectiva | **Top-down**, estética **cartoon colorida** (cores saturadas, contornos grossos) |
| Mecânica de rebatida | **Mini-game sequencial**: ÂNGULO → ESPAÇO → FORÇA → ESPAÇO |
| Movimento | Setas movem o jogador, restrito ao próprio campo |
| Modos | **M1 = 1P vs CPU (Torneio)** · **M2 = 2P local** · **M3 = Modo Treino** |
| Pontuação | **Tênis oficial**: 0-15-30-40-game · 6 games = set (com 2 de vantagem) · tie-break a 7 no 6-6 · melhor de 3 sets |
| Modo principal (M1) | **Torneio**: 🏖️ Rafael Nadal → 🌲 Flor Floresta → 🏟️ Estela Estádio |
| Recursos avançados | **High-score persistente** + **estatísticas simples** (aces e winners, contagem direta) |
| Assets | **Gerados via código Python** (`assets_generator.py`) com `pygame.draw`, exceto `assets/sprites/Nadal.png` |
| Resolução | 960×600, 60 FPS |

### Controles 1P
| Tecla | Ação |
|-------|------|
| ← → ↑ ↓ | Mover jogador |
| ESPAÇO | (1ª) trava ângulo · (2ª) trava força |
| P / ESC | Pausar |
| ENTER | Confirmar em menus |

### Controles 2P (mesmo teclado)
| Tecla | Ação |
|-------|------|
| W A S D | Mover Player 2 |
| SHIFT direito | (1ª) trava ângulo · (2ª) trava força do Player 2 |

### Modo Treino
| Tecla | Ação |
|-------|------|
| Mesmas do 1P | Jogar contra parede ou bot rebatedor |
| TAB | Alternar entre "parede" e "bot" |

---

## 2. Mecânica das Duas Barras Sequenciais

Quando a bola se aproxima do campo do jogador (`BARS_ACTIVATION_DISTANCE`), a HUD entra
em modo de mira. Fluxo de 4 estados:

- **`IDLE`** — apenas movimento livre.
- **`AIMING`** — barra de ângulo oscila; ESPAÇO trava o ângulo.
- **`POWERING`** — barra de força oscila (com sweet spot 70-90% em verde); ESPAÇO trava.
- **`LOCKED`** — barras congeladas por `SHOW_FROZEN_TIME`s; rebatida acontece quando a bola encosta no jogador.

Se o jogador **não travar a tempo** ou **não alcançar a bola**, conta como erro
(ponto para o adversário).

### Cálculo do vetor da bola (pseudocódigo)

```python
angle_locked = locked_angle_value      # entre AIM_MIN_ANGLE e AIM_MAX_ANGLE
power_locked = locked_power_value      # entre POWER_MIN e POWER_MAX

if SWEET_SPOT_LOW <= power_locked <= SWEET_SPOT_HIGH:
    angle_jitter = 0
    is_sweet = True
else:
    angle_jitter = random.uniform(-MISS_JITTER, MISS_JITTER)
    is_sweet = False

final_angle = angle_locked + angle_jitter
final_speed = BALL_BASE_SPEED + power_locked * (BALL_MAX_SPEED - BALL_BASE_SPEED)
direction_y = -1 if player.side == "bottom" else +1

ball.velocity = Vector2(
    sin(radians(final_angle)) * final_speed,
    cos(radians(final_angle)) * final_speed * direction_y,
)
```

---

## 3. Sistema de Pontuação Oficial (resumo executável)

> **O Codex DEVE seguir exatamente esta lógica** ao implementar `ScoreManager`.

### 3.1 Hierarquia
- **Ponto:** `0 → 15 → 30 → 40 → game`
- **Game:** primeiro a 4 pontos com diferença ≥ 2
- **Set:** primeiro a 6 games com diferença ≥ 2 (em 6-6, vai para tie-break)
- **Tie-break:** primeiro a 7 pontos com diferença ≥ 2
- **Match:** melhor de 3 sets

### 3.2 Lógica do Game (deuce/advantage)
```
Se ambos têm ≥ 3 pontos:
    diff = abs(p1 - p2)
    if diff == 0:  estado = "DEUCE"      (placar exibido "40-40")
    if diff == 1:  estado = "ADVANTAGE"  (placar "AD-40" ou "40-AD")
    if diff == 2:  vence quem tem mais   (game fecha, recomeça 0-0)
Senão:
    primeiro a 4 pontos vence o game.
```

### 3.3 Tie-break
- Pontuação simples (0, 1, 2, 3...).
- Primeiro a 7 com ≥ 2 de diferença vence o set 7-6.
- Em 6-6 no tie-break, joga-se até alguém abrir 2 pontos.

### 3.4 Saque
- Alterna a cada game.
- No tie-break, alterna a cada 2 pontos (após o primeiro do novo sacador).

### 3.5 Estatísticas SIMPLES (versão final do projeto)
Acumular durante a partida:
- **Aces:** saques onde o adversário não conseguiu rebater (passou direto pelo campo dele).
- **Winners:** rebatidas no sweet spot que resultaram em ponto direto (adversário não tocou).

> **NÃO implementar erros não forçados** — a distinção é complexa e fora de escopo.
> Aces e winners são contagens diretas e fáceis de detectar.

### 3.6 Interface obrigatória de `ScoreManager`
```python
class ScoreManager:
    """Gerencia pontuação oficial do tênis (15-30-40-game-set-match)."""

    def __init__(self, p1_name, p2_name): ...

    def add_point(self, winner_side: str, point_type: str = "normal"):
        """Registra um ponto e atualiza placar.
        winner_side: 'p1' ou 'p2'.
        point_type: 'ace' | 'winner' | 'normal'.
        """

    def current_game_score(self) -> tuple[str, str]:  # ex.: ("40", "AD")
    def current_set_games(self) -> tuple[int, int]:   # ex.: (5, 4)
    def sets_won(self) -> tuple[int, int]:            # ex.: (1, 0)
    def server(self) -> str:                          # "p1" ou "p2"
    def is_match_over(self) -> bool:
    def winner(self) -> str | None:
    def is_tiebreak(self) -> bool:
    def stats(self, side: str) -> dict:               # {"aces": int, "winners": int}
```

---

## 4. Estrutura de Arquivos

```
projeto_tenis/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── highscores.json         # high-score persistente
├── docs/
│   ├── design_doc.md           # rascunhos, esboços (evidência de colaboração — Obj 3 → A)
│   └── ai_usage.md             # registro detalhado de uso de IA por arquivo
├── assets/
│   └── sprites/
│       └── Nadal.png           # sprite externo do Rafael Nadal
└── src/
    ├── __init__.py
    ├── settings.py
    ├── game.py
    ├── assets_generator.py     # gera assets via pygame.draw e carrega sprites externos pontuais
    ├── entities/
    │   ├── __init__.py
    │   ├── player.py
    │   ├── ai_player.py
    │   ├── ball.py
    │   └── practice_bot.py     # M3
    ├── scenes/
    │   ├── __init__.py
    │   ├── base_scene.py
    │   ├── menu_scene.py
    │   ├── instructions_scene.py
    │   ├── tournament_scene.py
    │   ├── gameplay_scene.py
    │   ├── pause_scene.py
    │   ├── stats_scene.py      # estatísticas (aces, winners) ao fim do match
    │   └── game_over_scene.py
    ├── systems/
    │   ├── __init__.py
    │   ├── timing_bars.py      # mecânica sequencial
    │   ├── score_manager.py    # tênis real
    │   ├── stats_tracker.py    # aces e winners (simples)
    │   ├── physics.py
    │   ├── collision.py
    │   └── highscore.py        # leitura/escrita JSON
    └── utils/
        ├── __init__.py
        ├── asset_cache.py      # cacheia surfaces geradas pelo assets_generator
        ├── sound_manager.py    # SoundManager — sons gerados via pygame.sndarray (sintéticos)
        └── animations.py
```

### Sobre `assets_generator.py`
Quase todos os "sprites" são gerados em runtime via `pygame.draw` e cacheados. A exceção
é o Rafael Nadal, carregado de `assets/sprites/Nadal.png`. Estilo cartoon = formas
chapadas com **contorno preto grosso**.

Funções esperadas neste módulo:
- `make_court(scenery_id) -> pygame.Surface`
- `make_player_sprite(color) -> pygame.Surface`
- `make_ai_sprite(opponent_id) -> pygame.Surface` (carrega Nadal para `beach`; gera cores diferentes nos demais adversários)
- `make_ball() -> pygame.Surface`
- `make_trophy() -> pygame.Surface`
- `make_swing_animation_frames(color) -> list[pygame.Surface]` (3-5 frames)
- `make_button(text, color) -> pygame.Surface`

Sons também são sintéticos via `pygame.sndarray` ou `pygame.mixer.Sound` com waveforms simples.
**Justificativa para o README:** "Optamos por gerar a maior parte dos assets visuais
em código Python, mantendo o sprite do Rafael Nadal organizado em `assets/sprites/`."

### Regras invioláveis de arquitetura
1. Toda entidade interativa herda de `pygame.sprite.Sprite`.
2. Cenas implementam: `handle_events(events)`, `update(dt)`, `draw(surface)`, `next_scene()`.
3. Constantes ficam SOMENTE em `settings.py`.
4. Assets são gerados UMA vez por `asset_cache.py` no início do jogo.
5. Toda função/classe pública tem docstring (padrão Google, em português).
6. `clock.tick(FPS)` SOMENTE em `Game.run`.
7. `pygame.sprite.Group` para coleções; `pygame.sprite.collide_mask` para colisões precisas.
8. PEP 8 + nomes em inglês no código, comentários e docstrings em português.

---

## 5. `settings.py` — constantes obrigatórias

```python
"""Constantes globais do jogo de tênis cartoon."""

# Janela
WIDTH, HEIGHT = 960, 600
FPS = 60
TITLE = "Tennis Cartoon - DesSoft"

# Cores cartoon
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 60)
RED = (235, 80, 80)
BLUE = (90, 150, 235)
GREEN_SWEET = (80, 200, 100)
GREEN_LOCKED = (60, 180, 90)
GRAY_INACTIVE = (120, 120, 130)
ORANGE = (255, 150, 60)
HUD_BG = (20, 20, 30, 180)
LINE_OUTLINE = (40, 40, 60)

# Paleta dos cenários cartoon
SCENERY_COLORS = {
    "beach":   {"bg": (255, 220, 130), "court": (240, 200, 100), "lines": WHITE},
    "forest":  {"bg": (60, 130, 80),   "court": (90, 170, 100),  "lines": WHITE},
    "stadium": {"bg": (30, 90, 150),   "court": (50, 130, 200),  "lines": WHITE},
}

# Quadra
COURT_MARGIN = 60
NET_Y = HEIGHT // 2
NET_HEIGHT = 6

# Jogador
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_SPEED = 320
HIT_RADIUS = 70

# Bola
BALL_RADIUS = 10
BALL_BASE_SPEED = 300
BALL_MAX_SPEED = 720

# Mecânica das barras (SEQUENCIAL)
BAR_WIDTH = 280
BAR_HEIGHT = 20
BAR_SPACING = 12
AIM_MIN_ANGLE = -65
AIM_MAX_ANGLE = 65
AIM_OSC_SPEED = 220
POWER_MIN = 0.30
POWER_MAX = 1.00
POWER_OSC_SPEED = 1.6
SWEET_SPOT_LOW = 0.70
SWEET_SPOT_HIGH = 0.90
MISS_JITTER = 8.0
SHOW_FROZEN_TIME = 0.25

BARS_ACTIVATION_DISTANCE = 220

# Pontuação tênis real
GAME_TARGET_POINTS = 4
GAMES_TARGET_SET = 6
TIEBREAK_TARGET = 7
SETS_TO_WIN_MATCH = 2

# Adversários do torneio
TOURNAMENT_OPPONENTS = [
    {"id": "beach",   "name": "Rafael Nadal",   "reaction": 0.40, "aim_error": 14.0, "max_speed": 260, "color": (220, 110, 80)},
    {"id": "forest",  "name": "Flor Floresta",  "reaction": 0.25, "aim_error":  8.0, "max_speed": 320, "color": (140, 80, 200)},
    {"id": "stadium", "name": "Estela Estádio", "reaction": 0.12, "aim_error":  3.5, "max_speed": 400, "color": (60, 60, 60)},
]

# Caminhos
HIGHSCORE_PATH = "data/highscores.json"
```

---

# 🛠 PARTE PRINCIPAL — Tarefas por Componente

> **Filosofia desta seção:** cada componente do jogo é dividido em **3 sub-tarefas**,
> uma por desenvolvedor. Assim **todos mexem em todas as áreas do jogo**, ninguém fica
> "preso" a um pedaço, e os commits ficam naturalmente balanceados.
>
> Cada sub-tarefa tem um **prompt pronto para enviar ao Codex** (a equipe só copia, cola
> e revisa). O resultado de cada sub-tarefa é **um commit separado** assinado pelo dev
> responsável.
>
> **Os 3 devs são chamados de Dev1, Dev2, Dev3** — atribua os nomes reais aos papéis
> antes de começar.

## Componente A — Setup e Estrutura Base

### A.1 — Dev1: Estrutura de pastas e `settings.py`
**Commit sugerido:** `chore(setup): cria estrutura de pastas e settings.py`

**Prompt para o Codex:**
```
Crie a estrutura de pastas do projeto descrita na seção 4 do plano_jogo_tenis_codex.md
e o arquivo src/settings.py com TODAS as constantes da seção 5. Crie também os arquivos
__init__.py vazios em cada pacote, requirements.txt com pygame>=2.5, .gitignore para
Python e um README.md mínimo com título e nomes dos integrantes (placeholders).
NÃO crie nenhum outro arquivo de código nesta tarefa.
```

### A.2 — Dev2: `main.py` e classe `Game`
**Commit sugerido:** `feat(game): classe Game com loop principal e troca de cenas`

**Prompt para o Codex:**
```
Crie src/game.py com a classe Game (loop principal, clock.tick(FPS), gerenciamento de
cenas via change_scene) e main.py que apenas instancia Game e chama run(). Game deve
expor: self.screen, self.clock, self.running, self.scene, self.assets (placeholder dict),
self.sound_manager (None por enquanto). O método run() processa eventos com pygame.event.get(),
chama self.scene.handle_events(events), self.scene.update(dt), self.scene.draw(self.screen)
e pygame.display.flip(). Importe constantes APENAS de src/settings.py. Inclua docstrings
Google em português. Por enquanto a cena inicial pode ser uma cena placeholder simples
que apenas pinta a tela de uma cor.
```

### A.3 — Dev3: `BaseScene` abstrata
**Commit sugerido:** `feat(scenes): BaseScene abstrata com interface comum`

**Prompt para o Codex:**
```
Crie src/scenes/base_scene.py com a classe abstrata BaseScene (use abc.ABC). Métodos
abstratos: handle_events(self, events), update(self, dt), draw(self, surface),
next_scene(self) -> BaseScene | None. A classe deve receber `game` no construtor e
guardar como self.game. Inclua docstrings Google em português explicando contrato de
cada método. Não importe nenhuma cena concreta.
```

---

## Componente B — Geração e Carregamento de Assets

### B.1 — Dev2: Sprites de quadra e personagens
**Commit sugerido:** `feat(assets): gera quadras e sprites de jogadores via pygame.draw`

**Prompt para o Codex:**
```
Crie src/assets_generator.py com as funções make_court(scenery_id), make_player_sprite(color)
e make_ai_sprite(opponent_id). Estilo cartoon: cores chapadas das paletas em SCENERY_COLORS
(settings.py), contorno preto de 3px em todas as formas, sombra simples (offset (3, 3),
preto com alpha 60). make_court desenha a quadra (court_color), as linhas brancas das
quadras de tênis simples (limites + linha de saque + linha central) e a rede no centro.
make_player_sprite desenha um círculo (cabeça) sobre um retângulo arredondado (corpo) com
a cor recebida. make_ai_sprite carrega `assets/sprites/Nadal.png` para o adversário
`beach` e usa a cor do TOURNAMENT_OPPONENTS[opponent_id]["color"] nos demais.
Cada função retorna um pygame.Surface com tamanho apropriado e SRCALPHA. Inclua docstrings
Google em português.
```

### B.2 — Dev3: Sprites de bola, troféu e UI
**Commit sugerido:** `feat(assets): gera bola, troféu e botões via pygame.draw`

**Prompt para o Codex:**
```
Adicione em src/assets_generator.py as funções make_ball(), make_trophy() e
make_button(text, color, width, height). make_ball: círculo amarelo (YELLOW) com
contorno preto e a clássica linha curva branca (use pygame.draw.arc). make_trophy:
forma de troféu cartoon em dourado (~RGB 255,200,60) com base preta. make_button:
retângulo arredondado (use pygame.draw.rect com border_radius), contorno preto grosso,
texto centralizado em branco com fonte default em negrito. Todas retornam Surface com
SRCALPHA. Docstrings Google em português.
```

### B.3 — Dev1: Animação de rebatida e cache de assets
**Commit sugerido:** `feat(assets): animação de swing + asset_cache para reuso`

**Prompt para o Codex:**
```
Adicione em src/assets_generator.py a função make_swing_animation_frames(color) que
retorna uma lista de 4 pygame.Surface representando uma animação simples de rebatida
(player com braço estendido em ângulos diferentes — pode ser um retângulo extra rotacionado
saindo do corpo, simulando raquete). Crie também src/utils/asset_cache.py com a classe
AssetCache que tem um dicionário interno e métodos get(key, factory_fn): se key existe,
retorna; senão chama factory_fn(), guarda e retorna. Game (em src/game.py) deve
instanciar uma única AssetCache e armazenar em self.assets. Docstrings Google em português.
```

---

## Componente C — Bola e Física

### C.1 — Dev3: Classe `Ball` básica
**Commit sugerido:** `feat(ball): cria classe Ball com movimento e fricção`

**Prompt para o Codex:**
```
Crie src/entities/ball.py com a classe Ball herdando de pygame.sprite.Sprite. Atributos:
self.image (do AssetCache via make_ball), self.rect, self.mask (de pygame.mask.from_surface),
self.pos (pygame.math.Vector2), self.velocity (Vector2), self.last_hitter (str | None),
self.bounce_count (int). Métodos: __init__(asset_cache, start_pos), update(dt) que integra
pos += velocity * dt e atualiza rect.center, reset(server_side) que reposiciona a bola
no lado correto e zera velocidade. Importe constantes de src/settings.py. Docstrings
Google em português.
```

### C.2 — Dev1: Aplicação de rebatida
**Commit sugerido:** `feat(ball): apply_shot calcula vetor a partir de ângulo+força`

**Prompt para o Codex:**
```
Adicione à classe Ball (src/entities/ball.py) o método apply_shot(angle_deg, power,
side_origin, is_sweet_spot). Implemente exatamente o pseudocódigo da seção 2 do
plano_jogo_tenis_codex.md (cálculo de final_angle, final_speed, direction_y, novo
self.velocity como Vector2). Retorne True se a rebatida foi aplicada. Importe
constantes (BALL_BASE_SPEED, BALL_MAX_SPEED, MISS_JITTER, SWEET_SPOT_LOW/HIGH) de
settings. Docstring Google em português.
```

### C.3 — Dev2: Detecção de bordas e rede
**Commit sugerido:** `feat(physics): bounces e detecção de bola fora`

**Prompt para o Codex:**
```
Crie src/systems/physics.py com funções puras (sem classes): bounce_off_walls(ball)
que reflete velocity.x se a bola encosta nas bordas laterais (rect.left <= 0 ou
rect.right >= WIDTH), ajustando a posição para dentro. is_out_of_bounds(ball) -> str | None
retorna "top" se ball.rect.bottom < 0, "bottom" se ball.rect.top > HEIGHT, ou None.
hit_net(ball) -> bool retorna True se a bola cruza a linha NET_Y enquanto ainda está
muito perto dela (use uma tolerância de NET_HEIGHT). Importe constantes de settings.
Docstrings Google em português.
```

---

## Componente D — Mecânica das Barras de Timing

### D.1 — Dev2: Estado AIMING (barra de ângulo)
**Commit sugerido:** `feat(timing): TimingBars com estado AIMING`

**Prompt para o Codex:**
```
Crie src/systems/timing_bars.py com a classe TimingBars. Estados como constantes de classe:
STATE_IDLE, STATE_AIMING, STATE_POWERING, STATE_LOCKED. Construtor recebe owner_side
("bottom"|"top") e lock_key (código pygame). Atributos: self.state, self.aim_value (float),
self.aim_direction (+1 ou -1), self.power_value, self.power_direction, self.locked_angle,
self.locked_power, self.frozen_until. Implemente NESTA TAREFA apenas: activate() (vai para
AIMING e começa oscilação), update(dt) que oscila aim_value entre AIM_MIN_ANGLE e
AIM_MAX_ANGLE com velocidade AIM_OSC_SPEED graus/s usando aim_direction (inverte ao bater
nas extremidades), reset() (volta para IDLE), is_locked() (retorna False por enquanto),
is_active() (retorna self.state != IDLE). Outros métodos podem ser stubs.
Docstrings Google em português.
```

### D.2 — Dev3: Estado POWERING + travamento sequencial
**Commit sugerido:** `feat(timing): adiciona estado POWERING e travamento sequencial`

**Prompt para o Codex:**
```
Em src/systems/timing_bars.py, complete a classe TimingBars. Adicione no update(dt) a
oscilação de power_value entre POWER_MIN e POWER_MAX a velocidade POWER_OSC_SPEED quando
state == STATE_POWERING. Implemente handle_lock_press() -> bool: se state == AIMING,
salva self.locked_angle = self.aim_value, transita para POWERING (zera power_value) e
retorna True. Se state == POWERING, salva self.locked_power = self.power_value, transita
para LOCKED, marca self.frozen_until = pygame.time.get_ticks() + SHOW_FROZEN_TIME*1000,
retorna True. Caso contrário retorna False. Implemente get_locked_values() -> tuple|None
que retorna (locked_angle, locked_power) só se state == LOCKED, senão None. is_locked()
agora retorna state == LOCKED. is_sweet_spot() -> bool retorna True se SWEET_SPOT_LOW <=
locked_power <= SWEET_SPOT_HIGH. Atualize reset() para zerar tudo. Docstrings em português.
```

### D.3 — Dev1: Renderização cartoon das barras
**Commit sugerido:** `feat(timing): renderização cartoon das barras de ângulo e força`

**Prompt para o Codex:**
```
Em src/systems/timing_bars.py, implemente o método draw(surface) da classe TimingBars.
Estilo cartoon: BAR_WIDTH×BAR_HEIGHT, contorno preto de 3px (LINE_OUTLINE), cantos
arredondados (border_radius=8). Posicionar próximo à HUD do jogador (use owner_side
para escolher topo ou fundo). Barra de ângulo:
- fundo cinza claro
- cursor em GRAY_INACTIVE oscilando se state == IDLE/POWERING/LOCKED, em laranja vivo se AIMING
- se state >= POWERING, mostrar marca verde fixa em locked_angle
Barra de força (logo abaixo, com BAR_SPACING):
- fundo cinza claro
- pinta zona verde GREEN_SWEET entre SWEET_SPOT_LOW e SWEET_SPOT_HIGH (proporcional)
- cursor cinza inativo se IDLE/AIMING, laranja se POWERING, verde GREEN_LOCKED se LOCKED
Não desenhar nada se state == IDLE. Docstring Google em português.
```

---

## Componente E — Player e AIPlayer

### E.1 — Dev3: Classe `Player` (humano) com movimento
**Commit sugerido:** `feat(player): classe Player com movimento e input configurável`

**Prompt para o Codex:**
```
Crie src/entities/player.py com Player herdando de pygame.sprite.Sprite. Construtor:
__init__(self, asset_cache, side, controls, name="Jogador"). controls é um dict como:
{"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
"lock": pygame.K_SPACE}. Atributos: self.image (asset_cache.get para player_sprite),
self.rect, self.mask, self.side ("bottom"|"top"), self.controls, self.name, self.timing_bars
(instância de TimingBars), self.aim_state ("IDLE" inicialmente). Posição inicial: centro
horizontal, perto da borda inferior se side=="bottom" senão borda superior. Método
handle_input(self, keys) move o jogador via pygame.key.get_pressed(): vx, vy a partir das
teclas em self.controls, multiplicado por PLAYER_SPEED * dt (passe dt como parâmetro
adicional ou no update). Restrinja o movimento ao próprio campo (metade da quadra
respectiva, respeitando NET_Y). Método update(self, dt): atualiza posição e chama
self.timing_bars.update(dt). Importe constantes de settings. Docstrings em português.
```

### E.2 — Dev1: Integração Player com TimingBars + try_hit
**Commit sugerido:** `feat(player): integra TimingBars e implementa try_hit`

**Prompt para o Codex:**
```
Em src/entities/player.py, adicione: handle_event(self, event, ball) que reage a
KEYDOWN da tecla self.controls["lock"] chamando self.timing_bars.handle_lock_press().
can_hit(self, ball) -> bool retorna True se a distância entre self.rect.center e
ball.rect.center é <= HIT_RADIUS. try_hit(self, ball) -> str: se self.timing_bars.is_locked()
e self.can_hit(ball), pega get_locked_values(), chama ball.apply_shot(angle, power,
self.side, self.timing_bars.is_sweet_spot()), reseta self.timing_bars, e retorna
"winner" se is_sweet_spot() else "normal". Se is_locked() mas não pode bater (bola já
passou), retorna "miss". Senão retorna "no_hit". Atualize update(dt) para também
ativar timing_bars.activate() automaticamente quando a bola estiver a menos de
BARS_ACTIVATION_DISTANCE do jogador E a bola estiver vindo na direção dele
(verificar componente y de ball.velocity). Docstrings em português.
```

### E.3 — Dev2: Classe `AIPlayer`
**Commit sugerido:** `feat(ai): AIPlayer com 3 níveis de dificuldade`

**Prompt para o Codex:**
```
Crie src/entities/ai_player.py com AIPlayer herdando de Player. Construtor recebe
asset_cache, side, opponent_config (dict de TOURNAMENT_OPPONENTS) e chama super().__init__
com controls={} (não usa teclas). Atributos extras: self.opponent_config, self.reaction_timer,
self.target_x. Sobrescreve handle_input para fazer nada. Implementa decide(self, ball, dt)
que:
1. Decrementa self.reaction_timer; só age quando <= 0, depois reseta para opponent_config["reaction"].
2. Calcula target_x = ball.pos.x + random uniform(-aim_error, +aim_error).
3. Move-se em direção a target_x com velocidade limitada a opponent_config["max_speed"] * dt.
4. Quando a bola está a menos de HIT_RADIUS, simula uma rebatida: chama ball.apply_shot
   com ângulo aleatório (uniform AIM_MIN_ANGLE/AIM_MAX_ANGLE com viés para o lado oposto
   ao jogador humano) e power aleatório (uniform 0.5 a 1.0).
A IA NÃO usa TimingBars — bate diretamente. Sobrescreve update(dt, ball) para chamar
decide. Importe constantes. Docstrings em português.
```

---

## Componente F — Pontuação Tênis Real

### F.1 — Dev1: Lógica de game (0-15-30-40 + deuce/advantage)
**Commit sugerido:** `feat(score): ScoreManager - lógica de game com deuce/advantage`

**Prompt para o Codex:**
```
Crie src/systems/score_manager.py com ScoreManager. Construtor: __init__(p1_name, p2_name).
Atributos: self.p1_name, self.p2_name, self._game_points = {"p1": 0, "p2": 0},
self._set_games = {"p1": 0, "p2": 0}, self._sets_won = {"p1": 0, "p2": 0},
self._sets_history = []  (lista de tuplas (p1_games, p2_games)), self._server = "p1",
self._stats = {"p1": {"aces": 0, "winners": 0}, "p2": {"aces": 0, "winners": 0}}.
Implemente NESTA TAREFA apenas: add_point(winner_side, point_type="normal") que
incrementa _game_points[winner_side], atualiza self._stats se point_type in ("ace","winner"),
e chama um método interno _check_game_winner(). _check_game_winner(): se ambos têm >= 3,
diff = p1-p2. Se diff >= 2: vence p1 (zera _game_points, chama _on_game_won("p1")). Se
<= -2: vence p2. Senão (DEUCE/ADV) não fecha. Se algum tem >= 4 e diff >=2: vence. _on_game_won(side)
incrementa _set_games[side] (esta tarefa pode deixar stub para set check). Implemente também:
current_game_score() -> tuple[str,str] que retorna ("0","15","30","40","AD") ou ("40","40")
para deuce, considerando os casos de vantagem. stats(side) -> dict. Inclua um bloco
if __name__ == "__main__": com asserts: 4-0 game; 3-3→4-3 (AD)→4-4 (DEUCE)→5-4 (AD)→6-4 game;
3-0 não fecha (placar "40-0"). Docstrings em português.
```

### F.2 — Dev2: Lógica de set + tie-break
**Commit sugerido:** `feat(score): adiciona lógica de set e tie-break`

**Prompt para o Codex:**
```
Em src/systems/score_manager.py, complete _on_game_won(side): incrementa _set_games[side]
e chama _check_set_winner(). Implemente _check_set_winner: se max_games >= GAMES_TARGET_SET
e diff >= 2 → set fechado (chama _on_set_won(winner)). Se 6-6 → entra em modo tie-break
(self._is_tiebreak = True, _game_points zerados, mas no tie-break add_point soma direto
sem aplicar 0-15-30-40). Se em tie-break, _check_game_winner deve usar regra do tie-break
(>= TIEBREAK_TARGET com diff >= 2 vence o set 7-6 ou superior). _on_set_won(side):
incrementa _sets_won[side], adiciona tupla aos _sets_history, troca _server (alternância
a cada game já implementada também), zera _set_games e checa match. is_tiebreak() retorna
self._is_tiebreak. current_game_score() em tie-break retorna (str(p1), str(p2)) sem
conversão. Adicione asserts no __main__: simular 6 games seguidos sem vantagem → set 6-0;
simular ir até 6-6 → entra tiebreak; tiebreak 7-5 → set fecha 7-6. Docstrings em português.
```

### F.3 — Dev3: Match (melhor de 3) + alternância de saque + interface completa
**Commit sugerido:** `feat(score): match completo + alternância de saque`

**Prompt para o Codex:**
```
Em src/systems/score_manager.py, finalize: _on_set_won deve verificar se _sets_won[side]
>= SETS_TO_WIN_MATCH e setar self._match_over = True, self._match_winner = side.
Implemente: is_match_over() -> bool, winner() -> str|None, sets_won() -> tuple[int,int]
(p1, p2), current_set_games() -> tuple[int,int], server() -> str, is_tiebreak() -> bool.
Garanta que após cada game o saque alterna (self._server = "p2" if "p1" else "p1") ANTES
do próximo ponto. No tie-break, saque alterna a cada 2 pontos a partir do 1º. Adicione
asserts no __main__ para: vitória 2-0 em sets; vitória 2-1 em sets (com tie-break em um
deles); _server alterna corretamente a cada game; estatísticas (aces e winners) registradas.
Docstrings em português.
```

---

## Componente G — Colisões e StatsTracker

### G.1 — Dev2: Colisão jogador×bola com máscara
**Commit sugerido:** `feat(collision): jogador×bola com máscara e cooldown`

**Prompt para o Codex:**
```
Crie src/systems/collision.py com função player_hits_ball(player, ball, last_hit_time_ms,
cooldown_ms=200) -> bool. Usa pygame.sprite.collide_mask(player, ball). Se True E o tempo
desde last_hit_time_ms é >= cooldown_ms, retorna True. Senão False. O cooldown evita
múltiplas detecções da mesma colisão. Inclua também check_ball_out_of_bounds(ball) que
delega para physics.is_out_of_bounds. Docstrings em português.
```

### G.2 — Dev3: `StatsTracker` (aces e winners)
**Commit sugerido:** `feat(stats): StatsTracker simples (aces e winners)`

**Prompt para o Codex:**
```
Crie src/systems/stats_tracker.py com a classe StatsTracker. Construtor sem argumentos.
Atributos: self._stats = {"p1": {"aces": 0, "winners": 0}, "p2": {"aces": 0, "winners": 0}}.
Métodos: register_ace(side), register_winner(side), get(side) -> dict, reset(). Esta classe
é redundante com o que ScoreManager já guarda — sua função é ser uma fachada simples para
a UI consultar sem precisar conhecer ScoreManager por inteiro. Quando GameplayScene detectar
um ace ou winner, chama tanto stats_tracker.register_ace/winner quanto score_manager.add_point
com o point_type apropriado. Docstrings em português.
```

### G.3 — Dev1: `HighscoreManager`
**Commit sugerido:** `feat(highscore): leitura/escrita JSON com top 5`

**Prompt para o Codex:**
```
Crie src/systems/highscore.py com HighscoreManager. Construtor recebe path (default
HIGHSCORE_PATH de settings). Atributos: self._data com chaves "tournament", "2p",
"training" — cada uma é uma lista. Carregamento: tenta abrir e json.load; se arquivo
não existe ou JSON inválido, inicializa com listas vazias. add_tournament_record(name,
opponents_beaten) adiciona {"name": name, "opponents": opponents_beaten,
"date": ISO yyyy-mm-dd}, ordena por opponents desc, mantém top 5, salva. add_2p_record
e add_training_record análogos (training armazena maior_rally em vez de opponents).
get_top(category) -> list. save() escreve JSON com indent=2 em path. Inclua tratamento
de erro com try/except em torno do open. Docstrings em português.
```

---

## Componente H — Cenas (Menu, Instruções, Torneio)

### H.1 — Dev3: `MenuScene`
**Commit sugerido:** `feat(scenes): MenuScene cartoon com 5 opções`

**Prompt para o Codex:**
```
Crie src/scenes/menu_scene.py com MenuScene herdando de BaseScene. Opções (em ordem):
"Torneio (1P vs CPU)", "2 Jogadores Local", "Modo Treino", "Como Jogar", "Recordes", "Sair".
Atributo self.selected_index. handle_events: setas ↑↓ mudam selected_index, ENTER aciona,
ESC sai do jogo. update(dt) pode ser vazio. draw(surface): desenha fundo cartoon (gradiente
ou cor sólida YELLOW), título "TENNIS CARTOON" no topo (fonte grande, contorno preto), e os
botões usando assets.get(...) para o botão (asset_generator.make_button). O botão selecionado
tem cor ORANGE, demais BLUE. next_scene() retorna a próxima cena baseada na opção (placeholders
podem retornar None enquanto cenas não existem). Importe constantes. Docstrings em português.
```

### H.2 — Dev1: `InstructionsScene`
**Commit sugerido:** `feat(scenes): InstructionsScene explicando barras sequenciais`

**Prompt para o Codex:**
```
Crie src/scenes/instructions_scene.py com InstructionsScene herdando de BaseScene. Mostra
em texto explicativo (várias linhas) os controles (←→↑↓ mover, ESPAÇO travar) e a mecânica
sequencial: "1. Quando a bola se aproxima, a BARRA DE ÂNGULO aparece e oscila. Pressione
ESPAÇO para travar a direção. 2. Em seguida a BARRA DE FORÇA oscila. Acerte na zona VERDE
para um winner! Pressione ESPAÇO de novo para finalizar." Inclua também regras de pontuação
em uma frase. ENTER ou ESC volta ao menu. draw deve ter fundo cartoon, título "COMO JOGAR",
texto centralizado, e uma demonstração visual: desenhe duas barras (ângulo e força) com
cursores parados em posições ilustrativas usando pygame.draw. Docstrings em português.
```

### H.3 — Dev2: `TournamentScene`
**Commit sugerido:** `feat(scenes): TournamentScene com mapa dos 3 adversários`

**Prompt para o Codex:**
```
Crie src/scenes/tournament_scene.py com TournamentScene herdando de BaseScene. Lê o
progresso do torneio de game.tournament_progress (int de 0 a 3 = quantos adversários
vencidos). Desenha 3 cards horizontais, um para cada item de TOURNAMENT_OPPONENTS, com
o sprite da IA (asset_generator.make_ai_sprite), o nome, uma breve descrição e um indicador
visual: ✓ verde se já vencido (índice < tournament_progress), [JOGAR] em laranja se é o
próximo (índice == tournament_progress), 🔒 cinza se ainda bloqueado. ENTER/ESPAÇO inicia
partida contra o próximo adversário desbloqueado, transicionando para GameplayScene com
mode="1p" e opponent_id=TOURNAMENT_OPPONENTS[tournament_progress]["id"]. Setas ←→ permitem
visualizar info detalhada de cada card. ESC volta ao MenuScene. Quando tournament_progress
== 3, mostrar troféu (asset_generator.make_trophy) e botão "VOLTAR AO MENU". Docstrings
em português.
```

---

## Componente I — `GameplayScene` (núcleo do jogo)

### I.1 — Dev2: Setup da `GameplayScene` (1P vs CPU)
**Commit sugerido:** `feat(gameplay): GameplayScene integra Player + AI + Bola`

**Prompt para o Codex:**
```
Crie src/scenes/gameplay_scene.py com GameplayScene herdando de BaseScene. Construtor
recebe game e mode (str: "1p"|"2p"|"training") e opponent_id (str|None). Inicializa:
- self.scenery = opponent_id or "beach" (fallback)
- self.court_surface (asset_cache.get com make_court(scenery))
- self.player1 = Player(asset_cache, "bottom", CONTROLS_P1, "Você")
- Se mode=="1p": self.player2 = AIPlayer(asset_cache, "top", config do oponente). Stub
  para outros modes nesta tarefa.
- self.ball = Ball(asset_cache, start_pos no centro, descendo).
- self.score_manager = ScoreManager("Você", oponente_name).
- self.stats_tracker = StatsTracker().
- self.last_hit_time = 0.
draw(): desenha self.court_surface, depois self.player1, self.player2, self.ball, e
chama self.player1.timing_bars.draw(surface) e self.player2.timing_bars.draw quando aplicável.
update(dt): chama player1.update(dt), player2.update(dt) (com ball para AIPlayer).
ball.update(dt). physics.bounce_off_walls(ball). Trata colisão jogador×bola com cooldown.
Esta tarefa NÃO precisa implementar pontos ainda. Importe e use TODAS as classes existentes.
Docstrings em português.
```

### I.2 — Dev3: Lógica de pontuação dentro do gameplay
**Commit sugerido:** `feat(gameplay): integra ScoreManager e detecção de pontos`

**Prompt para o Codex:**
```
Em src/scenes/gameplay_scene.py, adicione no update(dt): após ball.update, chamar
physics.is_out_of_bounds(ball). Se retornar "top" → ponto para player1. Se "bottom" →
ponto para player2. Determinar point_type: se ball.last_hitter == lado_vencedor e
ball.bounce_count == 0 (bola direta sem quicar no campo do adversário), checar se foi
sweet_spot — se sim, point_type="winner"; senão "normal". Se ball.was_served and
ball.last_hitter == lado_vencedor and ball.bounce_count == 0, considerar "ace". Chamar
score_manager.add_point(winner_side, point_type), e stats_tracker.register_ace/winner
quando aplicável. Após cada ponto, chamar ball.reset(server_side=score_manager.server()),
zerar timing_bars dos jogadores e tocar som "score". Se score_manager.is_match_over(),
transicionar para StatsScene (próxima sub-tarefa). Docstrings em português.
```

### I.3 — Dev1: HUD da gameplay (placar tênis real)
**Commit sugerido:** `feat(hud): placar 15-30-40 + games + sets + nomes`

**Prompt para o Codex:**
```
Em src/scenes/gameplay_scene.py, adicione método draw_hud(surface) e chame-o no fim de
draw(). HUD deve renderizar (estilo cartoon — retângulo HUD_BG semi-transparente no topo
da tela com border_radius e contorno preto):
- Nome dos dois jogadores (esquerda).
- current_game_score() do ScoreManager (centro, fonte grande).
- current_set_games() (ex.: "3 - 2") (à direita).
- sets_won() como bolinhas preenchidas (ex.: ●○ vs ●● para 1-2).
- Indicador de saque: ícone de bola amarela ao lado de quem está sacando (server()).
- Se is_tiebreak(), exibir "TIE-BREAK" em destaque.
Use a fonte default em negrito. Importe constantes. Docstring em português.
```

---

## Componente J — Cenas de Pause, Stats e GameOver

### J.1 — Dev3: `PauseScene`
**Commit sugerido:** `feat(scenes): PauseScene como overlay`

**Prompt para o Codex:**
```
Crie src/scenes/pause_scene.py com PauseScene herdando de BaseScene. Construtor recebe
game e previous_scene (referência à GameplayScene para retornar). draw() desenha primeiro
self.previous_scene.draw(surface) (mantém a gameplay congelada por trás), depois um
overlay preto com alpha 150 cobrindo tudo, depois um painel central com 2 botões:
"CONTINUAR" e "MENU PRINCIPAL". Setas ↑↓ + ENTER navegam. update(dt) é vazio (jogo
pausado). ESC ou P retorna ao previous_scene. Docstrings em português.
```

### J.2 — Dev1: `StatsScene`
**Commit sugerido:** `feat(scenes): StatsScene exibindo aces e winners`

**Prompt para o Codex:**
```
Crie src/scenes/stats_scene.py com StatsScene herdando de BaseScene. Construtor recebe
game, score_manager e stats_tracker. draw(): título "ESTATÍSTICAS DA PARTIDA", duas
colunas (uma por jogador) mostrando:
- Nome
- Sets vencidos
- Aces (com ícone)
- Winners (com ícone)
- Histórico de sets (ex.: "6-4 · 7-6 · 6-2") usando _sets_history do ScoreManager
ENTER → vai para GameOverScene. Estilo cartoon, contornos pretos grossos, cores do tema.
Docstrings em português.
```

### J.3 — Dev2: `GameOverScene` + integração com highscore
**Commit sugerido:** `feat(scenes): GameOverScene com troféu e salvamento de highscore`

**Prompt para o Codex:**
```
Crie src/scenes/game_over_scene.py com GameOverScene herdando de BaseScene. Construtor
recebe game, winner_name, mode e (opcionalmente) opponents_beaten para o modo torneio.
Se mode=="1p" e jogador venceu: desenha troféu (asset_cache + make_trophy) animado
(pulando levemente com pygame.time.get_ticks()), incrementa game.tournament_progress.
Sempre: chama game.highscore_manager.add_*_record com os dados apropriados (no fim do
match). Texto "VITÓRIA!" ou "DERROTA" em fonte grande. ENTER volta ao MenuScene (ou
TournamentScene se estiver em torneio e ainda houver adversários). Importe constantes.
Docstrings em português.
```

---

## Componente K — Áudio (sons sintéticos)

### K.1 — Dev1: `SoundManager` e som de hit/bounce
**Commit sugerido:** `feat(audio): SoundManager com hit e bounce sintéticos`

**Prompt para o Codex:**
```
Crie src/utils/sound_manager.py com a classe SoundManager. Construtor inicializa
pygame.mixer (try/except — se falhar, modo silencioso). Gera os sons em runtime via
numpy + pygame.sndarray.make_sound:
- hit: senoide 600Hz com envelope decaindo, ~80ms.
- bounce: senoide 300Hz, ~60ms.
Cada som é um pygame.mixer.Sound armazenado em self._sounds. Método play(name) toca
o som; ignora silenciosamente se não existe. Se numpy não estiver disponível, faça
fallback para sons no-op (passa silenciosamente). Adicione numpy>=1.20 ao requirements.txt.
Docstrings em português.
```

### K.2 — Dev2: Sons de score/ace/menu
**Commit sugerido:** `feat(audio): sons sintéticos de score, ace e menu_click`

**Prompt para o Codex:**
```
Em src/utils/sound_manager.py, adicione mais sons gerados:
- score: 2 senoides em sequência (ré + sol, ~150ms cada) — uma vitória curta.
- ace: 3 senoides ascendentes (dó-mi-sol, 100ms cada) — celebração maior.
- menu_click: ruído branco curto (50ms) com filtro passa-baixa simples (média móvel).
Use as mesmas técnicas (numpy + sndarray). Docstrings em português.
```

### K.3 — Dev3: Música ambiente (loops sintéticos por cenário)
**Commit sugerido:** `feat(audio): músicas ambiente sintéticas por cenário`

**Prompt para o Codex:**
```
Em src/utils/sound_manager.py, adicione método play_music(scenery_id) que toca um loop
de 4-8 segundos gerado proceduralmente. Use uma sequência de notas simples diferente
para cada cenário (beach: tons de ukulele simulado com senoides; forest: tons graves
de marimba; stadium: padrão rítmico mais marcial). Use pygame.mixer.music ou um Sound
em loop com play(loops=-1). Método stop_music() para chamar entre cenas. Caso a geração
seja muito complexa, crie loops simples de notas senoidais variadas — o objetivo é apenas
ter ambiente sonoro distinto. Docstring em português.
```

---

## Componente L — Modos M2 e M3

### L.1 — Dev1: M2 — `GameplayScene` com 2 jogadores
**Commit sugerido:** `feat(gameplay): suporta mode="2p" com 2 jogadores no mesmo teclado`

**Prompt para o Codex:**
```
Em src/scenes/gameplay_scene.py, no construtor, quando mode=="2p" instancie self.player2
como Player normal (não AIPlayer) com controls={"up": K_w, "down": K_s, "left": K_a,
"right": K_d, "lock": K_RSHIFT} e name="Player 2". Garanta que ambos players têm timing_bars
visíveis e funcionando independentemente. Em handle_events, encaminhe eventos de teclado
para ambos os players (cada um filtra seu próprio lock_key). HUD passa a mostrar nomes
configuráveis (deixar como "Player 1" e "Player 2" por padrão). Atualize MenuScene para
permitir entrar em 2P (apontar para GameplayScene com mode="2p"). Highscore: ao fim do
match, chamar add_2p_record com vencedor. Docstring em português.
```

### L.2 — Dev2: M3 — `PracticeBot` e modo treino
**Commit sugerido:** `feat(practice): PracticeBot e mode="training"`

**Prompt para o Codex:**
```
Crie src/entities/practice_bot.py com PracticeBot herdando de pygame.sprite.Sprite.
Comportamento: persegue a bola horizontalmente em velocidade média (~250 px/s) e quando
está perto, sempre rebate de volta com ângulo aleatório uniform(-30, 30) e power 0.6.
Não tem score. Em GameplayScene, quando mode=="training", instancie PracticeBot como
self.player2 e desabilite ScoreManager (substitua por contador self.rally_count que
incrementa a cada rebatida bem-sucedida do jogador humano). HUD mostra "RALLY: N" em vez
de placar. ESC ou TAB transitam para mode parede futuramente. Atualize MenuScene para
incluir entrada para Modo Treino. Docstring em português.
```

### L.3 — Dev3: M3 — Modo parede + persistência de rally
**Commit sugerido:** `feat(practice): modo parede + salva maior rally`

**Prompt para o Codex:**
```
Em src/scenes/gameplay_scene.py, quando mode=="training", suportar self.training_submode
("bot" ou "wall") alternado com TAB. No modo "wall", não instancia player2; em vez disso
modifica physics: a borda superior reflete a bola (basta inverter velocity.y quando
ball.rect.top <= COURT_MARGIN, em vez de marcar como out_of_bounds). Quando o jogador
falha em rebater (bola sai), reseta self.rally_count = 0 e chama
game.highscore_manager.add_training_record(name, max_rally) se foi maior que o anterior.
HUD mostra também "RECORDE: N" lendo do highscore. Docstring em português.
```

---

## 6. Sprints Sugeridas

| Sprint | Período | Componentes a fechar |
|--------|---------|---------------------|
| 1 | até 11/05 | A · B · C · D (M1 estrutural) |
| 2 | até 18/05 | E · F · G · H · I · J (M1 jogável end-to-end) |
| 3 | até 22/05 | K · L (M2 e M3) + assets cartoon refinados |
| 4 | 23–25/05 | Polimento · README · vídeo · ajustes finais |

**Importante:** dentro de cada sprint os 3 devs trabalham em paralelo nos componentes
ativos, cada um pegando sua sub-tarefa. Sub-tarefas de um mesmo componente podem ser
feitas em paralelo se forem independentes (ex.: D.1 e D.3 dependem do esqueleto da
classe TimingBars criado em D.1).

---

## 7. Convenções de Git

- **Mensagens:** [Conventional Commits] — `feat(escopo): descrição`, `fix(escopo): descrição`, `docs:`, `refactor:`, `style:`, `chore:`.
- **Branches:** `feat/devN-nome-da-feature`, `fix/devN-bug`.
- **PRs:** ao menos 1 review de outro dev antes do merge.
- **Balanceamento:** rodar `git shortlog -sn` antes da entrega — cada dev com volume similar (~12-15 commits cada com base nas sub-tarefas listadas).
- **Histórico:** com 12 sub-tarefas por dev distribuídas entre os componentes A-L, cada um faz um pouco de tudo (assets, gameplay, cenas, áudio, sistemas).

---

## 8. Checklist da Rubrica × Onde está Implementado

| Requisito | Onde |
|-----------|------|
| Tela de menu/início | `MenuScene` (H.1) |
| Tela informativa | `InstructionsScene` (H.2) |
| Tela de fim | `GameOverScene` (J.3) |
| Múltiplas fases | **Torneio progressivo** com 3 adversários (`TournamentScene`, H.3) |
| Pontuação | **Tênis oficial** (Componente F: F.1+F.2+F.3) |
| Animações | swing animation (B.3) + rastro da bola |
| Efeitos sonoros + música | `SoundManager` (Componente K) |
| Botão de pause | `PauseScene` (J.1) |
| Inimigos com comportamento | `AIPlayer` 3 níveis (E.3) |
| Mecânica diferenciada | **Sweet spot da barra de força** + barras sequenciais (Componente D) |
| Colisões coerentes | `Collision` com `collide_mask` (G.1) |
| FPS controlado | `Game.run` (A.2) |
| Orientação a objetos | tudo herda de Sprite/BaseScene |
| Múltiplos arquivos | estrutura completa em `src/{entities,scenes,systems,utils}/` |
| Docstrings | obrigatórias em todas as sub-tarefas (Google, em português) |
| Recurso "acima do esperado" | **Tênis real (15-30-40-deuce-AD-tiebreak)** + **estatísticas (aces, winners)** + **3 modos** + **highscore persistente** + **assets gerados em código** |
| Distribuição de Git balanceada | sub-tarefas distribuídas garantem ~12 commits por dev cobrindo todas as áreas |
| Implementação acima do esperado | tênis oficial é mais complexo que pong simples; assets em código mostram criatividade |

---

## 9. Instruções para o Codex (LEIA ANTES DE CADA TAREFA)

Quando o Codex receber qualquer prompt das sub-tarefas acima, ele **DEVE**:

1. **Respeitar a estrutura de pastas** descrita na seção 4 — nunca criar arquivos fora dela.
2. **Importar constantes apenas de `src/settings.py`** — proibido valor hardcoded.
3. **Toda função/classe pública tem docstring Google em português:**
   ```python
   def add_point(self, winner_side, point_type="normal"):
       """Registra um ponto e atualiza o placar.

       Args:
           winner_side (str): "p1" ou "p2".
           point_type (str): "ace" | "winner" | "normal".

       Returns:
           dict: snapshot do estado atual do placar.
       """
   ```
4. **PEP 8**: `snake_case` para funções/variáveis, `PascalCase` para classes.
5. **Nomes em portugues e simples no código**, comentários em português.
6. **Toda entidade interativa herda de `pygame.sprite.Sprite`** com `super().__init__()`.
7. **Assets via `asset_cache.get(...)` chamando `assets_generator.*`** — nunca carregar arquivos externos.
8. **`pygame.sprite.collide_mask`** para colisões.
9. **Cenas DEVEM ter os 4 métodos**: `handle_events(events)`, `update(dt)`, `draw(surface)`, `next_scene()`.
10. **`dt` obrigatório em `update`**; lógica baseada em tempo deve multiplicar por `dt`.
11. **`clock.tick(FPS)` SOMENTE em `Game.run`** (componente A.2).
12. **Sem variáveis globais** fora de `settings.py`.
13. **Falhas graciosas**: assets que falham → fallback colorido; JSON inexistente → criar vazio.
14. **Comentário-cabeçalho em trechos significativos**:
    `# Implementação inicial gerada por IA (Codex), revisada pela equipe.`
15. **Respeitar a ordem dos milestones** — não implementar features de M2/M3 dentro de M1.
16. **Mecânica das barras é SEQUENCIAL** — primeira pressão de ESPAÇO trava ângulo, segunda trava força. NUNCA simultânea.
17. **Pontuação é TÊNIS OFICIAL** (15-30-40-game-set-match-tiebreak-deuce-advantage) — implementar conforme seção 3.
18. **Estatísticas SIMPLES** — apenas aces e winners. **NÃO implementar erros não forçados.**
19. **Cada sub-tarefa = 1 commit isolado** — não misturar escopo de outras sub-tarefas no mesmo PR.

---

## 10. README.md — Esqueleto a ser preenchido

```markdown
# 🎾 Tennis Cartoon — Projeto Final DesSoft

Jogo de tênis 2D top-down em estilo cartoon, com **mecânica única de mini-game de
timing sequencial** (trave o ângulo, depois a força!) e **pontuação oficial do tênis**
(15-30-40-deuce-advantage-tiebreak, melhor de 3 sets).

## Desenvolvedor
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
| Pause | P / ESC | – |

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
**A maior parte dos gráficos foi gerada em código Python via `pygame.draw`** (formas
geométricas cartoon coloridas). O sprite do Rafael Nadal fica em
`assets/sprites/Nadal.png`. Veja `src/assets_generator.py`.
Os sons também são sintetizados em runtime via numpy + pygame.sndarray.

## Dependências
- Python 3.10+
- pygame >= 2.5
- numpy >= 1.20

## Uso de Inteligência Artificial Generativa
Este projeto foi planejado com auxílio de uma LLM (Claude) que produziu o documento
`plano_jogo_tenis_codex.md` com a divisão de tarefas, e cada sub-tarefa foi enviada
como prompt para o Codex (ChatGPT). Detalhamento por arquivo está em `docs/ai_usage.md`.

Toda a equipe revisou criticamente o código gerado, validou seu funcionamento e é
capaz de explicar cada trecho. Bugs introduzidos pela IA foram corrigidos pela equipe,
conforme orientação do curso.
```

---

## 11. `docs/ai_usage.md` — Esqueleto

```markdown
# Registro de Uso de IA Generativa

Cada sub-tarefa do plano foi enviada como prompt ao Codex/ChatGPT. Listamos abaixo
cada arquivo, qual sub-tarefa o gerou, qual dev integrou, e quais ajustes manuais foram
feitos após o código vir da IA.

## src/settings.py
- Sub-tarefa: A.1
- Dev integrador: Dev1
- Ajustes manuais: nenhum (constantes vieram do plano).

## src/game.py
- Sub-tarefa: A.2
- Dev integrador: Dev2
- Ajustes manuais: ajuste do delta time para milissegundos.

## src/assets_generator.py — make_court, make_player_sprite, make_ai_sprite
- Sub-tarefa: B.1
- Dev integrador: Dev2
- Ajustes manuais: paleta de cores ajustada para melhor contraste.

(...continuar para cada um dos ~30+ arquivos do projeto)
```

---

## 12. Critérios de "Pronto" Antes de Entregar

- [ ] `python main.py` roda sem erros após `pip install -r requirements.txt` em máquina limpa.
- [ ] **M1 completo:** torneio 1P vs CPU jogável nos 3 cenários, com pontuação tênis oficial.
- [ ] **M2 completo:** 2P local funcionando.
- [ ] **M3 completo:** Modo treino (parede e bot) funcionando.
- [ ] Mecânica sequencial das barras funciona (ângulo → ESPAÇO → força → ESPAÇO).
- [ ] `ScoreManager` validado por asserts (deuce/AD/set 7-5/tie-break/match 2-1).
- [ ] Menu, instruções, mapa do torneio, gameplay, pause, stats, game over — todos navegáveis.
- [ ] Pelo menos 3 músicas distintas (uma por cenário) + 5 efeitos sonoros sintéticos.
- [ ] Animação de rebatida do jogador.
- [ ] Progresso do torneio salvo entre execuções.
- [ ] Estatísticas (aces, winners) exibidas em `StatsScene`.
- [ ] README completo com vídeo, instruções, integrantes, seção de IA generativa.
- [ ] `docs/ai_usage.md` listando origem de cada arquivo gerado por IA.
- [ ] `git shortlog -sn` mostra commits balanceados (~12 por dev distribuídos por todas as áreas).
- [ ] `docs/design_doc.md` com esboços (evidência de colaboração além do código).
- [ ] Código sem erros (`python -m pyflakes src/` limpo).
- [ ] Todas as classes e funções públicas têm docstring.

---

*Documento de referência para o Codex e a equipe. Atualizar conforme decisões evoluírem.*
