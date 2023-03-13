# Candidate number: 244118
# constants.py
#
# this file contains constants used by different parts of the checkers game.
# It also loads assets.

import pygame
import pygame.freetype
import os

# board constants in pixels
WIDTH = 800
HEIGHT = 800
NUM_ROWS = 8
NUM_COLS = 8

TILE_SIZE = int(HEIGHT / NUM_ROWS)

PIECE_RADIUS = TILE_SIZE * 0.4
PIECE_RADIUS_SELECTED = PIECE_RADIUS * 1.1

KING_ICON_SIZE = 400
KING_ICON_SCALE = int(PIECE_RADIUS*1.3)

# misc game constants
FPS = 60

# colors in RGB
WHITE = (255, 255, 255, .1)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (230, 230, 230)
GREEN = (0, 204, 102)
DARKER_GREEN = (0, 153, 77)

ORANGE = (255, 204, 128)
DARKER_ORANGE = (255, 153, 0)

EASY_COLOR_SELECTED = (51, 102, 255)
EASY_COLOR = (153, 179, 255)

MEDIUM_COLOR_SELECTED = (153, 51, 255)
MEDIUM_COLOR = (204, 153, 255)

HARD_COLOR_SELECTED = (255, 0, 0)
HARD_COLOR = (255, 128, 128)

CAPTION = "Welcome to Checkers"

base_path = os.path.dirname(__file__)
dark_background_path = os.path.join(base_path, "../assets/cherry-wood-background.jpeg")
light_background_path = os.path.join(base_path, "../assets/light-wood-background.jpeg")
DARK_BACKGROUND = pygame.image.load(dark_background_path)
LIGHT_BACKGROUND = pygame.image.load(light_background_path)

black_king_path = os.path.join(base_path, "../assets/black-king.png")
white_king_path = os.path.join(base_path, "../assets/white-king.png")
BLACK_KING_ICON_UNSCALED = pygame.image.load(black_king_path)
WHITE_KING_ICON_UNSCALED = pygame.image.load(white_king_path)

BLACK_KING_ICON = pygame.transform.scale(BLACK_KING_ICON_UNSCALED, (KING_ICON_SCALE, KING_ICON_SCALE))
WHITE_KING_ICON = pygame.transform.scale(WHITE_KING_ICON_UNSCALED, (KING_ICON_SCALE, KING_ICON_SCALE))

default_font = pygame.font.get_default_font()
game_font = pygame.freetype.SysFont(default_font, 0)