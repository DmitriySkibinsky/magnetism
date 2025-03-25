from cfg import *
import numpy as np
from power_lines import compute_field


def draw_focus_lines(surface):
    """Рисует силовые линии с эффектом фокусировки на указанной поверхности."""
    for cx, cy, q in charges:
        color = BLUE if q > 0 else RED
        pygame.draw.circle(surface, color, (int(cx), int(cy)), 15, 2)

        for angle in np.linspace(0, 2 * np.pi, START_POINTS):
            x, y = cx + 20 * np.cos(angle), cy + 20 * np.sin(angle)
            points = []

            for _ in range(ITERATIONS):
                Ex, Ey = compute_field(x, y)
                norm = np.hypot(Ex, Ey)
                if norm < 1e-3:
                    break

                Ex, Ey = Ex / norm, Ey / norm
                if other_charges := [(ox, oy) for ox, oy, _ in charges if (ox, oy) != (cx, cy)]:
                    min_dist = min(np.hypot(x - ox, y - oy) for ox, oy in other_charges)
                    step = max(STEP * min_dist / 50, 1)
                else:
                    step = STEP

                x += step * Ex
                y += step * Ey
                points.append((x, y))

                if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
                    break

            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, 1)

    if len(charges) >= 2:
        center_x = sum(c[0] for c in charges) / len(charges)
        center_y = sum(c[1] for c in charges) / len(charges)
        pygame.draw.circle(surface, GREEN, (int(center_x), int(center_y)), 10, 2)