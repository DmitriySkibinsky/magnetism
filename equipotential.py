from cfg import *
from power_lines import compute_field
import numpy as np


def draw_equipotential_lines(surface):
    """Рисует эквипотенциальные линии на указанной поверхности."""
    for cx, cy, q in charges:
        i = 0
        for angle in np.linspace(0, 2 * np.pi, START_POINTS):
            x, y = cx + 20 * np.cos(angle), cy + 20 * np.sin(angle)
            points = []

            for _ in range(ITERATIONS):
                Ex, Ey = compute_field(x, y)
                norm = np.hypot(Ex, Ey)
                if norm < 1e-3:
                    break

                Ex, Ey = -Ey / norm, Ex / norm
                x += STEP * Ex
                y += STEP * Ey

                points.append((x, y))
            i += 1

            if len(points) > 1 and i % 15 == 0:
                pygame.draw.lines(surface, BLACK, False, points, 1)


def compute_potential(x, y):
    """Вычисляет электрический потенциал в точке (x,y)"""
    potential = 0.0
    for cx, cy, q in charges:
        dx = x - cx
        dy = y - cy
        r = max(np.sqrt(dx*dx + dy*dy), 0.1)  # Защита от деления на 0
        potential += q / r
    return potential