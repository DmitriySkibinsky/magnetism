from cfg import *
import numpy as np

def compute_potential(x, y, scale=1.0):
    """Вычисляет электрический потенциал в точке (x, y) с учетом масштаба."""
    total = 0.0
    for cx, cy, q in charges:
        dx = x - cx
        dy = y - cy
        distance = max(1, (dx**2 + dy**2)**0.5)  # избегаем деления на 0
        total += q / (distance * scale)  # применяем масштаб к расстоянию
    return total / 100

def draw_potential_map(surface, radius_scale=1.0):
    """Рисует цветовую карту потенциала на указанной поверхности с масштабированием радиуса."""
    cell_size = 10

    grid_width = WIDTH // cell_size
    grid_height = HEIGHT // cell_size

    min_potential = float('inf')
    max_potential = -float('inf')

    potentials = np.zeros((grid_height, grid_width))

    for i in range(grid_height):
        for j in range(grid_width):
            x = j * cell_size + cell_size // 2
            y = i * cell_size + cell_size // 2
            potential = compute_potential(x, y, radius_scale)
            potentials[i, j] = potential
            if potential < min_potential:
                min_potential = potential
            if potential > max_potential:
                max_potential = potential

    # Нормализуем и рисуем
    for i in range(grid_height):
        for j in range(grid_width):
            x = j * cell_size
            y = i * cell_size
            potential = potentials[i, j]

            if max_potential != min_potential:
                normalized = (potential - min_potential) / (max_potential - min_potential)
            else:
                normalized = 0.5

            if normalized < 0.5:
                blue_intensity = int(255 * (1 - 2 * normalized))
                color = (0, 0, blue_intensity)
            else:
                red_intensity = int(255 * (2 * (normalized - 0.5)))
                color = (red_intensity, 0, 0)

            pygame.draw.rect(surface, color, (x, y, cell_size, cell_size))

    # Рисуем заряды поверх карты
    for x, y, q in charges:
        color = RED if q > 0 else BLUE
        pygame.draw.circle(surface, color, (int(x), int(y)), 15)

