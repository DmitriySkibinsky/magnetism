from cfg import *
import numpy as np
import pygame
import math
from scipy.integrate import odeint

# Глобальные константы
ELECTRON_RADIUS = 8  # радиус электрона в пикселях
TRAJECTORY_WIDTH = 4  # ширина траектории в пикселях
RING_WIDTH = 2  # ширина кольца в пикселях
RING_LENGTH_SCALE = 10000  # масштаб длины кольца (чем больше, тем длиннее линия)
ANIMATION_DURATION = 8000  # продолжительность анимации в мс

# Физические константы
e = 1.602e-19  # заряд электрона [Кл]
m_e = 9.109e-31  # масса электрона [кг]
eps0 = 8.854e-12  # электрическая постоянная [Ф/м]

# Конфигурация колец (теперь z - горизонтальная координата)
rings = [
    {'radius': 0.02, 'charge': 1e-10, 'z_pos': -0.005},  # Левое кольцо
    {'radius': 0.02, 'charge': 1e-10, 'z_pos': -0.01},  # Левое кольцо
    {'radius': 0.02, 'charge': 1e-10, 'z_pos': -0.015},  # Левое кольцо
    {'radius': 0.02, 'charge': 1e-10, 'z_pos': -0.02},  # Левое кольцо

    {'radius': 0.02, 'charge': 1e-10, 'z_pos': 0.0},  # Центральное кольцо
    {'radius': 0.02, 'charge': 1e-10, 'z_pos': 0.005},  # Центральное кольцо
    {'radius': 0.02, 'charge': 1e-10, 'z_pos': 0.01},  # Центральное кольцо


    {'radius': 0.015, 'charge': 1e-9, 'z_pos': 0.015},  # Правое кольцо
    {'radius': 0.015, 'charge': 1e-9, 'z_pos': 0.02},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.0225},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.025},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.0275},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.03},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.0325},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.035},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.0375},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.04},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.0425},  # Правое кольцо
    {'radius': 0.013, 'charge': 1e-11, 'z_pos': 0.045},  # Правое кольцо

]

# Электроны (начальное положение и скорость)
electrons = [
    {'initial_pos': [-0.04, -0.007], 'initial_vel': [8.5e6, 2e5]},
    {'initial_pos': [-0.04, -0.003], 'initial_vel': [8.5e6, 2e5]},  # Верхний электрон
    {'initial_pos': [-0.04, 0.0001], 'initial_vel': [8.2e6, 0]},  # Центральный электрон
    {'initial_pos': [-0.04, 0.003], 'initial_vel': [8.5e6, 0]},  # Нижний электрон
    {'initial_pos': [-0.04, 0.008], 'initial_vel': [8.5e6, -2e5]},  # Дополнительный электрон
    {'initial_pos': [-0.04, 0.012], 'initial_vel': [8.5e6, -2e5]}  # Дополнительный электрон
]

# Цвета для электронов и их траекторий
electron_colors = [
    RED,
    (0, 180, 0),  # зеленый
    (255, 128, 0),  # оранжевый
    (0, 180, 180),  # бирюзовый
    (180, 0, 180),  # фиолетовый
    LIGHT_GRAY
]

# Глобальные переменные для хранения траекторий и времени последнего обновления
trajectories_data = None
last_update_time = 0


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
        t2 = z ** 2 + (R + ro) ** 2 #квадрат расстояния между точкой, в которой мы вычисляем поле, и точкой на кольце
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
    ro, z, v_ro, v_z = y

    # Если достигли фокусировки (например, z > 0.04), фиксируем движение вдоль оси z
    #if z > 0.04:
    #    return [0, v_z, 0, 0]  # v_ro = 0, движение только по оси z

    E_ro, E_z, _, _ = field_E(q_rings, R_rings, ro, z)

    # Сила, действующая на электрон (F = qE)
    F_ro = -e * E_ro
    F_z = -e * E_z

    # Ускорение (a = F/m)
    a_ro = F_ro / m_e
    a_z = F_z / m_e

    return [v_ro, v_z, a_ro, a_z]



def simulate_electrons_trajectories(rings, electrons):
    """Моделирование траекторий электронов через систему колец"""
    global trajectories_data

    t_max = 3e-8  # время симуляции [с]
    n_steps = 5000  # Количество шагов
    t = np.linspace(0, t_max, n_steps)

    R_rings = [ring['radius'] for ring in rings]
    q_rings = [ring['charge'] for ring in rings]

    trajectories = []
    valid_indices = []  # Индексы точек, где траектория движется вперед

    for electron in electrons:
        y0 = [
            electron['initial_pos'][1],  # ro (вертикальная координата)
            electron['initial_pos'][0],  # z (горизонтальная координата)
            electron['initial_vel'][1],  # v_ro
            electron['initial_vel'][0]  # v_z
        ]

        sol = odeint(electron_motion, y0, t, args=(q_rings, R_rings))
        trajectory = sol[:, :2]  # Берем только ro и z

        # Определяем, где траектория начинает идти назад
        z_values = trajectory[:, 1]  # z-координаты

        forward_indices = []
        prev_z = z_values[0]
        for i, z in enumerate(z_values):
            if z >= prev_z or i < 10:  # Позволяем небольшие колебания в начале
                forward_indices.append(i)
                prev_z = z
            else:
                break  # Прекращаем при движении назад

        trajectories.append(trajectory[:forward_indices[-1] + 1] if forward_indices else trajectory)

    trajectories_data = (t, trajectories)


def draw_focus_lines(surface):
    """Рисует траектории электронов и кольца с анимацией движения"""
    global trajectories_data, last_update_time

    # Инициализация траекторий при первом вызове
    if trajectories_data is None:
        simulate_electrons_trajectories(rings, electrons)
        last_update_time = pygame.time.get_ticks()

    t, trajectories = trajectories_data

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
    current_time = pygame.time.get_ticks()
    progress = (current_time - last_update_time) / ANIMATION_DURATION

    # Сброс анимации по завершении цикла
    if progress >= 1.0:
        last_update_time = current_time
        progress = 0.0

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

        # Рисуем траекторию
        if len(screen_points) > 1:
            # Полная траектория (бледная)
            faded_color = (color[0] // 4 + 192, color[1] // 4 + 192, color[2] // 4 + 192)
            pygame.draw.lines(surface, faded_color, False, screen_points, 1)

            # Анимированная часть траектории
            current_index = min(int(progress * len(screen_points)), len(screen_points) - 1)

            # Плавная интерполяция между точками
            if current_index > 0:
                partial_progress = (progress * len(screen_points)) % 1.0
                if current_index < len(screen_points) - 1 and partial_progress > 0:
                    x1, y1 = screen_points[current_index]
                    x2, y2 = screen_points[current_index + 1]
                    current_x = x1 + (x2 - x1) * partial_progress
                    current_y = y1 + (y2 - y1) * partial_progress
                    screen_points_interp = screen_points[:current_index + 1] + [(current_x, current_y)]
                else:
                    screen_points_interp = screen_points[:current_index + 1]

                pygame.draw.lines(surface, color, False, screen_points_interp, TRAJECTORY_WIDTH)

                # Рисуем "электрон" (кружок) в текущей позиции
                if screen_points_interp:
                    pygame.draw.circle(surface, color, screen_points_interp[-1], ELECTRON_RADIUS)
                    pygame.draw.circle(surface, WHITE, screen_points_interp[-1], ELECTRON_RADIUS - 3)

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