import pygame

# Размеры окна
WIDTH, HEIGHT = 1500, 800
charges = []
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Параметры по умолчанию
STEP = 5
ITERATIONS = 1000
START_POINTS = 35

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)

# Настройки меню
MENU_WIDTH = 200
SLIDER_WIDTH = 160
SLIDER_HEIGHT = 20
SLIDER_KNOB_RADIUS = 8