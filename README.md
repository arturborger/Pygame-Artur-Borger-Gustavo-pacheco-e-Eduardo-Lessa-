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
