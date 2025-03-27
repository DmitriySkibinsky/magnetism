import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from matplotlib.colors import hsv_to_rgb

# Константы
e = 1.602e-19  # заряд электрона [Кл]
m_e = 9.109e-31  # масса электрона [кг]
eps0 = 8.854e-12  # электрическая постоянная [Ф/м]


def CEL1(t):
    """Эллиптический интеграл 1-го рода"""
    if t < 1.e-8:
        return 1.e5
    t1 = (((0.01451196212 * t + 0.03742563713) * t + 0.03590092383) * t
          + 0.09666344259) * t + 1.38629436112
    t2 = (((0.00441787012 * t + 0.03328355346) * t + 0.06880248576) * t
          + 0.12498593597) * t + 0.5
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
    # Время моделирования
    t_max = 2e-8  # время симуляции [с]
    n_steps = 3000
    t = np.linspace(0, t_max, n_steps)

    # Разделяем параметры колец
    R_rings = [ring['radius'] for ring in rings]
    q_rings = [ring['charge'] for ring in rings]
    z_rings = [ring['z_pos'] for ring in rings]

    # Создаем фигуру
    plt.figure(figsize=(12, 8))

    # Рисуем кольца
    for R, z_pos in zip(R_rings, z_rings):
        theta = np.linspace(0, 2 * np.pi, 100)
        ring_x = z_pos * np.ones_like(theta)
        ring_y = R * np.sin(theta)
        plt.plot(ring_x, ring_y, 'r-', linewidth=2)

    # Генерируем разные цвета для электронов
    colors = hsv_to_rgb(np.array([(i / len(electrons), 0.8, 0.8) for i in range(len(electrons))]))

    # Моделируем траектории для каждого электрона
    for i, electron in enumerate(electrons):
        initial_pos = electron['initial_pos']  # [ro, z]
        initial_vel = electron['initial_vel']  # [v_ro, v_z]

        # Решение уравнений движения
        solution = odeint(electron_motion,
                          initial_pos + initial_vel,
                          t,
                          args=(q_rings, R_rings))

        # Рисуем траекторию
        plt.plot(solution[:, 1], solution[:, 0], '-', color=colors[i],
                 label=f'Электрон {i + 1}')

        # Рисуем начальную точку
        plt.plot(initial_pos[1], initial_pos[0], 'o', color=colors[i], markersize=8)

    plt.xlabel('Ось Z (м)')
    plt.ylabel('Ось ρ (м)')
    plt.title('Движение электронов через систему заряженных колец')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()


# Пример использования:
if __name__ == "__main__":
    # Определяем кольца (радиус в метрах, заряд в Кулонах, положение по Z)
    rings = [
        {'radius': 0.01, 'charge': 1e-10, 'z_pos': 0.0},
        {'radius': 0.005, 'charge': -0.5e-10, 'z_pos': 0.02},
        {'radius': 0.008, 'charge': 0.3e-10, 'z_pos': -0.015}
    ]

    # Определяем электроны (начальное положение и скорость)
    electrons = [
        {'initial_pos': [-0.001, -0.04], 'initial_vel': [0.5e5, 2.5e6]},
        {'initial_pos': [0.000, -0.04], 'initial_vel': [0.5e5, 2.2e6]},
        {'initial_pos': [0.001, -0.04], 'initial_vel': [0.5e5, 2.5e6]},
        {'initial_pos': [0.002, -0.04], 'initial_vel': [0.5e5, 2.5e6]}
    ]

    # Запускаем симуляцию
    simulate_electrons_trajectories(rings, electrons)