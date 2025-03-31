from cfg import *
import numpy as np
import pygame
import math
from scipy.integrate import odeint

# Глобальные константы
ELECTRON_RADIUS = 5  # радиус электрона в пикселях
TRAJECTORY_WIDTH = 2  # ширина траектории в пикселях
RING_WIDTH = 2       # ширина кольца в пикселях
RING_LENGTH_SCALE = 3000  # масштаб длины кольца (чем больше, тем длиннее линия)

# Физические константы
e = 1.602e-19  # заряд электрона [Кл]
m_e = 9.109e-31  # масса электрона [кг]
eps0 = 8.854e-12  # электрическая постоянная [Ф/м]

# Конфигурация колец (теперь z - горизонтальная координата)
rings = [
    {'radius': 0.01, 'charge': 1e-10, 'z_pos': 0.0},  # Центральное кольцо
    {'radius': 0.01, 'charge': 1e-10, 'z_pos': 0.02},  # Правое кольцо
    {'radius': 0.01, 'charge': 1e-10, 'z_pos': -0.02}  # Левое кольцо
]

# Электроны (начальное положение и скорость)
electrons = [
    {'initial_pos': [-0.04, -0.001], 'initial_vel': [2.5e6, 0.5e5]},  # Верхний электрон
    {'initial_pos': [-0.04, 0.000], 'initial_vel': [2.2e6, 0.5e5]},  # Центральный электрон
    {'initial_pos': [-0.04, 0.001], 'initial_vel': [2.5e6, 0.5e5]},  # Нижний электрон
    {'initial_pos': [-0.04, 0.002], 'initial_vel': [2.5e6, 0.5e5]}  # Дополнительный электрон
]

# Цвета для электронов и их траекторий
electron_colors = [
    (0, 180, 0),  # зеленый
    (255, 128, 0),  # оранжевый
    (0, 180, 180),  # бирюзовый
    (180, 0, 180)  # фиолетовый
]


def CEL1(t):
    """Эллиптический интеграл 1-го рода"""
    if t < 1.e-8:
        return 1.e5
    t1 = (((0.01451196212 * t + 0.03742563713) * t + 0.03590092383) * t + 0.09666344259) * t + 1.38629436112
    t2 = (((0.00441787012 * t + 0.03328355346) * t + 0.06880248576) * t + 0.12498593597) * t + 0.5
    return t1 - t2 * np.log(t)


def CEL2(t):
    """Эллиптический интеграл 2-го рода"""
    if t < 1.e-8:
        return 0
    t1 = (((0.01736506451 * t + 0.04757383546) * t + 0.06260601220) * t + 0.44325141463) * t + 1
    t2 = (((0.00526449639 * t + 0.04069697526) * t + 0.09200180037) * t + 0.24998368310) * t
    return t1 - t2 * np.log(t)


def field_E(q_rings, R_rings, ro, z):
    """Вычисление поля системы заряженных колец"""
    E_ro_total = 0
    E_z_total = 0
    E_total = 0
    fi_total = 0

    for q, R in zip(q_rings, R_rings):
        if R == 0:
            continue

        k = 1 / (4 * np.pi * eps0)  # коэффициент из закона Кулона
        t = q * k / np.pi
        t2 = z ** 2 + (R + ro) ** 2
        kk = 1 - 4 * R * ro / t2
        K = CEL1(kk)
        Ell = CEL2(kk)

        E_ro = 0
        if ro != 0:
            E_ro = t * (K - Ell * (R ** 2 + z ** 2 - ro ** 2) /
                        ((R - ro) ** 2 + z ** 2)) / (ro * np.sqrt(t2))

        E_z = 2 * t * (z * Ell / ((R - ro) ** 2 + z ** 2)) / np.sqrt(t2)
        E = np.sqrt(E_ro ** 2 + E_z ** 2)
        fi = 2 * t * K / np.sqrt(t2)

        E_ro_total += E_ro
        E_z_total += E_z
        E_total += E
        fi_total += fi

    return E_ro_total, E_z_total, E_total, fi_total


def electron_motion(y, t, q_rings, R_rings):
    """Уравнения движения электрона в поле системы колец"""
    ro, z, v_ro, v_z = y

    E_ro, E_z, _, _ = field_E(q_rings, R_rings, ro, z)

    # Сила, действующая на электрон (F = qE)
    F_ro = -e * E_ro  # минус, т.к. электрон отрицательно заряжен
    F_z = -e * E_z

    # Ускорение (a = F/m)
    a_ro = F_ro / m_e
    a_z = F_z / m_e

    return [v_ro, v_z, a_ro, a_z]


def simulate_electrons_trajectories(rings, electrons):
    """Моделирование траекторий электронов через систему колец"""
    t_max = 3e-8  # время симуляции [с]
    n_steps = 5000  # Увеличили количество шагов для более плавных траекторий
    t = np.linspace(0, t_max, n_steps)

    R_rings = [ring['radius'] for ring in rings]
    q_rings = [ring['charge'] for ring in rings]
    z_rings = [ring['z_pos'] for ring in rings]

    trajectories = []

    for electron in electrons:
        y0 = [
            electron['initial_pos'][1],  # ro (вертикальная координата)
            electron['initial_pos'][0],  # z (горизонтальная координата)
            electron['initial_vel'][1],  # v_ro
            electron['initial_vel'][0]  # v_z
        ]

        sol = odeint(electron_motion, y0, t, args=(q_rings, R_rings))
        trajectory = sol[:, :2]  # Берем только ro и z
        trajectories.append(trajectory)

    return t, trajectories


def draw_focus_lines(surface):
    """Рисует траектории электронов и кольца с анимацией движения"""
    t, trajectories = simulate_electrons_trajectories(rings, electrons)

    # Настройка масштабирования
    visible_width = 0.12  # Видимая область по горизонтали (12 см)
    visible_height = 0.06  # Видимая область по вертикали (6 см)

    scale_x = WIDTH / visible_width
    scale_y = HEIGHT / visible_height

    # Центрирование
    min_z = min(electron['initial_pos'][0] for electron in electrons)
    offset_x = -min_z * scale_x * 0.9
    offset_y = HEIGHT // 2

    # Очистка поверхности
    surface.fill(WHITE)

    # Рисуем кольца (вертикальные линии)
    for ring in rings:
        x_pos = offset_x + ring['z_pos'] * scale_x
        if 0 <= x_pos <= WIDTH:
            color = RED if ring['charge'] > 0 else BLUE
            # Длина линии зависит от радиуса кольца
            line_length = ring['radius'] * RING_LENGTH_SCALE
            pygame.draw.line(surface, color,
                             (x_pos, offset_y - line_length),
                             (x_pos, offset_y + line_length), RING_WIDTH)

            # Подписи зарядов
            if x_pos > 30 and x_pos < WIDTH - 30:
                font = pygame.font.SysFont("Arial", 10)
                charge_text = f"{abs(ring['charge']):.0e}C"
                text_surface = font.render(charge_text, True, BLACK)
                surface.blit(text_surface, (x_pos - 15, offset_y + line_length + 5))

    # Анимация движения электронов
    for i, trajectory in enumerate(trajectories):
        color = electron_colors[i % len(electron_colors)]

        # Конвертируем все точки траектории в экранные координаты
        screen_points = []
        for point in trajectory:
            ro, z = point
            x_px = offset_x + z * scale_x
            y_px = offset_y + ro * scale_y
            if -50 < x_px < WIDTH + 50 and -50 < y_px < HEIGHT + 50:
                screen_points.append((x_px, y_px))

        # Рисуем траекторию постепенно
        if len(screen_points) > 1:
            # Полная траектория (бледная)
            faded_color = (color[0] // 4 + 192, color[1] // 4 + 192, color[2] // 4 + 192)
            pygame.draw.lines(surface, faded_color, False, screen_points, 1)

            # Текущая позиция анимации (используем время для анимации)
            current_time = pygame.time.get_ticks() % 5000  # 5 секунд на полную анимацию
            progress = current_time / 5000  # от 0 до 1
            current_index = int(progress * (len(screen_points) - 1))

            # Рисуем часть траектории до текущей точки
            if current_index > 1:
                pygame.draw.lines(surface, color, False, screen_points[:current_index+1], TRAJECTORY_WIDTH)

            # Рисуем "электрон" (кружок) в текущей позиции
            if current_index < len(screen_points):
                pygame.draw.circle(surface, color, screen_points[current_index], ELECTRON_RADIUS)
                pygame.draw.circle(surface, WHITE, screen_points[current_index], ELECTRON_RADIUS-3)

    # Начальные позиции электронов
    for i, electron in enumerate(electrons):
        x_px = offset_x + electron['initial_pos'][0] * scale_x
        y_px = offset_y + electron['initial_pos'][1] * scale_y
        if 0 <= x_px <= WIDTH and 0 <= y_px <= HEIGHT:
            pygame.draw.circle(surface, BLACK, (x_px, y_px), 2)

    # Подписи осей
    font = pygame.font.SysFont("Arial", 12)
    # Ось Z (горизонтальная)
    pygame.draw.line(surface, BLACK, (20, HEIGHT - 20), (WIDTH - 20, HEIGHT - 20), 1)
    pygame.draw.polygon(surface, BLACK,
                        [(WIDTH - 25, HEIGHT - 25), (WIDTH - 20, HEIGHT - 20), (WIDTH - 25, HEIGHT - 15)])
    surface.blit(font.render("z", True, BLACK), (WIDTH - 15, HEIGHT - 25))

    # Ось ro (вертикальная)
    pygame.draw.line(surface, BLACK, (20, HEIGHT - 20), (20, 20), 2)
    pygame.draw.polygon(surface, BLACK, [(15, 25), (20, 20), (25, 25)])
    surface.blit(font.render("ro", True, BLACK), (25, 15))