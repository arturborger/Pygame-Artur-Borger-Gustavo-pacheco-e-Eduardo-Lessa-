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
GRAY_LIGHT = (220, 220, 230)
ORANGE = (255, 150, 60)
HUD_BG = (20, 20, 30, 180)
LINE_OUTLINE = (40, 40, 60)

# Paleta dos cenários cartoon
SCENERY_COLORS = {
    "beach": {"bg": (255, 220, 130), "court": (240, 200, 100), "lines": WHITE},
    "forest": {"bg": (60, 130, 80), "court": (90, 170, 100), "lines": WHITE},
    "stadium": {"bg": (30, 90, 150), "court": (50, 130, 200), "lines": WHITE},
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
BAR_OUTLINE_WIDTH = 3
BAR_BORDER_RADIUS = 8
BAR_CURSOR_WIDTH = 8
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
    {
        "id": "beach",
        "name": "Pedro Praia",
        "reaction": 0.40,
        "aim_error": 14.0,
        "max_speed": 260,
        "color": (220, 110, 80),
    },
    {
        "id": "forest",
        "name": "Flor Floresta",
        "reaction": 0.25,
        "aim_error": 8.0,
        "max_speed": 320,
        "color": (140, 80, 200),
    },
    {
        "id": "stadium",
        "name": "Estela Estádio",
        "reaction": 0.12,
        "aim_error": 3.5,
        "max_speed": 400,
        "color": (60, 60, 60),
    },
]

# Caminhos
HIGHSCORE_PATH = "data/highscores.json"
