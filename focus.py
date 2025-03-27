from cfg import *
import numpy as np
import pygame
import math

# Константы
ELECTRON_CHARGE = -1.6e-19
EPSILON_0 = 8.85e-12
K = 1 / (4 * math.pi * EPSILON_0)

# Цвета
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

class ChargedRing:
    def __init__(self, x, y, charge, radius=50):
        self.x = x
        self.y = y
        self.charge = charge
        self.radius = radius

    def compute_field(self, px, py):
        """Вычисление электрического поля в точке (px, py)"""
        dx = px - self.x
        dy = py - self.y
        ro = math.sqrt(dx**2 + dy**2)  # Расстояние в плоскости
        z = 0  # 2D-плоскость

        if self.radius == 0:
            return 0, 0

        t = self.charge * K / math.pi
        t2 = (self.radius + ro)**2

        kk = 1 - 4 * self.radius * ro / t2
        kk = max(0.01, min(kk, 0.99))  # Ограничение на kk

        K_ell = self.cel1(kk)
        E_ell = self.cel2(kk)

        E_ro = 0
        if ro != 0:
            numerator = (K_ell - E_ell * (self.radius**2 - ro**2) / ((self.radius - ro)**2))
            E_ro = t * numerator / (ro * math.sqrt(t2))

        E_z = 2 * t * (E_ell / ((self.radius - ro)**2)) / math.sqrt(t2)

        angle = math.atan2(dy, dx) if ro != 0 else 0
        Ex = E_ro * math.cos(angle)
        Ey = E_ro * math.sin(angle)

        return Ex, Ey

    def cel1(self, t):
        """Полный эллиптический интеграл 1-го рода"""
        if t < 1e-8:
            return 1e5
        t1 = (((0.0145 * t + 0.0374) * t + 0.0359) * t + 0.0966) * t + 1.386
        t2 = (((0.0044 * t + 0.0333) * t + 0.0688) * t + 0.1249) * t + 0.5
        return t1 - t2 * math.log(t)

    def cel2(self, t):
        """Полный эллиптический интеграл 2-го рода"""
        if t < 1e-8:
            return 0
        t1 = (((0.0173 * t + 0.0475) * t + 0.0626) * t + 0.4432) * t + 1
        t2 = (((0.0052 * t + 0.0407) * t + 0.0920) * t + 0.2499) * t
        return t1 - t2 * math.log(t)


def draw_focus_lines(surface):
    """Рисует заряженные кольца и их влияние на электроны"""
    rings = []
    electrons = []

    # Создаём кольца и электроны
    for cx, cy, q in charges:
        if abs(q) > 1e-9:  # Заряженные кольца
            rings.append(ChargedRing(cx, cy, q, 50))
        elif q == -1:  # Электроны
            electrons.append((cx, cy))

    # Если нет электронов, добавляем их вручную
    if len(electrons) != 5:
        electrons = [(100, HEIGHT / 2 - 100 + i * 50) for i in range(5)]

    print("Созданные кольца:", [(r.x, r.y, r.charge, r.radius) for r in rings])

    # Рисуем кольца
    for ring in rings:
        pygame.draw.circle(surface, BLUE if ring.charge > 0 else RED,
                           (int(ring.x), int(ring.y)), int(ring.radius), 2)

    # Двигаем электроны
    for ex, ey in electrons:
        points = []
        x, y = ex, ey
        velocity = np.array([3.0, 0.0])  # Скорость электрона

        for _ in range(ITERATIONS * 2):
            points.append((x, y))

            # Считаем поле от всех колец
            total_Ex, total_Ey = 0.0, 0.0
            for ring in rings:
                Ex, Ey = ring.compute_field(x, y)
                total_Ex += Ex
                total_Ey += Ey

            print(f"Электрон ({x:.1f}, {y:.1f}): E=({total_Ex:.2e}, {total_Ey:.2e})")

            # Обновляем скорость
            charge_mass_ratio = -1.76e11  # q/m электрона
            ax = charge_mass_ratio * total_Ex
            ay = charge_mass_ratio * total_Ey

            velocity[0] += ax * 0.05
            velocity[1] += ay * 0.05

            # Обновляем позицию
            x += velocity[0]
            y += velocity[1]

            # Если вылетает за экран — останавливаем
            if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
                break

        if len(points) > 1:
            pygame.draw.lines(surface, GREEN, False, points, 1)

    # Рисуем электроны
    for ex, ey in electrons:
        pygame.draw.circle(surface, BLACK, (int(ex), int(ey)), 5)
