# 🎾 Tennis Cartoon — Projeto Final DesSoft

Jogo de tênis 2D top-down em estilo cartoon, com **mecânica única de mini-game de
timing sequencial** (trave o ângulo, depois a força!) e **pontuação oficial do tênis**
(15-30-40-deuce-advantage-tiebreak, 1 set por partida).

## Desenvolvedor

- Artur Borger

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
tie-break a 7 quando 6-6 · **1 set vence a partida**.

## Estatísticas

Ao fim de cada partida você vê: aces e winners de cada jogador.

## Assets

**A maior parte dos gráficos foi gerada em código Python via `pygame.draw`** (formas
geométricas cartoon coloridas). Os sprites do Rafael Nadal, do Roger Federer e do
Novak Djokovic ficam em `assets/sprites/Nadal.png`, `assets/sprites/Federer.png` e
`assets/sprites/Djokovic.png`. Veja `src/assets_generator.py`.
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
