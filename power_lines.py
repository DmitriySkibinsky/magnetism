import pygame
import numpy as np
from cfg import *

def draw_charges():
    """Рисует заряды на экране."""
    for x, y, charge in charges:
        color = RED if charge > 0 else BLUE
        pygame.draw.circle(screen, color, (x, y), 15)

def compute_field(x, y):
    """Вычисляет вектор поля в точке (x, y)."""
    Ex, Ey = 0, 0
    for cx, cy, q in charges:
        dx, dy = x - cx, y - cy
        r2 = dx ** 2 + dy ** 2
        if r2 < 10:
            r2 = 10
        r = np.sqrt(r2)
        Ex += q * dx / r2
        Ey += q * dy / r2
    return Ex, Ey

def draw_field_lines(surface):
    """Рисует плавные силовые линии на указанной поверхности."""
    for cx, cy, q in charges:
        for angle in np.linspace(0, 2 * np.pi, START_POINTS):
            x, y = cx + 10 * np.cos(angle), cy + 10 * np.sin(angle)
            points = []

            for _ in range(ITERATIONS):
                Ex, Ey = compute_field(x, y)
                norm = np.hypot(Ex, Ey)
                if norm < 1e-3:
                    break

                Ex, Ey = Ex / norm, Ey / norm
                x += STEP * Ex
                y += STEP * Ey

                points.append((x, y))

            if len(points) > 1:
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