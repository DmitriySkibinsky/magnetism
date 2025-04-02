import pygame
import numpy as np
from cfg import *
from power_lines import *
from equipotential import *
from focus import *
from potential_map import *

# Инициализация Pygame
pygame.init()
pygame.display.set_caption("Магнитное поле")
draw_lines = False
mode = "field"  # Режим отображения: "field" - силовые линии, "equipotential" - эквипотенциальные линии

# Зоны кнопок
dropdown_rect = pygame.Rect(WIDTH - 150, 10, 140, 30)
button_build_rect = pygame.Rect(WIDTH - 150, 50, 140, 30)
button_reset_rect = pygame.Rect(WIDTH - 150, 90, 140, 30)  # Новая кнопка сброса
dropdown_options = ["Силовые линии", "Эквипотенциальные", "Фокусировка", "Карта потенциала"]
dropdown_active = False
selected_option = 0

# Поверхности для хранения построенных линий
field_lines_surface = None
equipotential_lines_surface = None
focus_lines_surface = None
potential_map_surface = None


def draw_buttons():
    """Рисует кнопки на экране."""
    # Рисуем выпадающее меню
    pygame.draw.rect(screen, GREEN, dropdown_rect, border_radius=5)
    font = pygame.font.SysFont("Arial", 24)
    text_dropdown = font.render(dropdown_options[selected_option], True, WHITE)
    screen.blit(text_dropdown, (dropdown_rect.x + 10, dropdown_rect.y + 5))

    # Рисуем кнопку "Построить"
    pygame.draw.rect(screen, BLUE, button_build_rect, border_radius=5)
    text_build = font.render("Построить", True, WHITE)
    screen.blit(text_build, (button_build_rect.x + 10, button_build_rect.y + 5))

    # Рисуем кнопку "Сброс" с красным фоном
    pygame.draw.rect(screen, RED, button_reset_rect, border_radius=5)
    text_reset = font.render("Сброс", True, WHITE)
    screen.blit(text_reset, (button_reset_rect.x + 40, button_reset_rect.y + 5))

    # Рисуем стрелку вниз для выпадающего меню
    if dropdown_active:
        for i, option in enumerate(dropdown_options):
            option_rect = pygame.Rect(WIDTH - 150, 40 + i * 30, 140, 30)
            pygame.draw.rect(screen, GREEN, option_rect, border_radius=5)
            text_option = font.render(option, True, WHITE)
            screen.blit(text_option, (option_rect.x + 10, option_rect.y + 5))


def build_field_lines():
    """Строит силовые линии один раз и сохраняет на поверхности"""
    global field_lines_surface
    field_lines_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    field_lines_surface.fill((0, 0, 0, 0))
    draw_field_lines(field_lines_surface)


def build_equipotential_lines():
    """Строит эквипотенциальные линии один раз и сохраняет на поверхности"""
    global equipotential_lines_surface
    equipotential_lines_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    equipotential_lines_surface.fill((0, 0, 0, 0))
    draw_equipotential_lines(equipotential_lines_surface)


def build_focus_lines():
    """Строит линии фокусировки один раз и сохраняет на поверхности"""
    global focus_lines_surface
    focus_lines_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    focus_lines_surface.fill((0, 0, 0, 0))
    draw_focus_lines(focus_lines_surface)


def build_potential_map():
    """Строит карту потенциала один раз и сохраняет на поверхности"""
    global potential_map_surface
    potential_map_surface = pygame.Surface((WIDTH, HEIGHT))
    potential_map_surface.fill(WHITE)
    draw_potential_map(potential_map_surface)


def reset_simulation():
    """Полностью сбрасывает симуляцию"""
    global draw_lines, field_lines_surface, equipotential_lines_surface, focus_lines_surface, potential_map_surface, charges
    draw_lines = False
    charges.clear()  # Очищаем список зарядов
    field_lines_surface = None
    equipotential_lines_surface = None
    focus_lines_surface = None
    potential_map_surface = None


def main():
    global draw_lines, mode, dropdown_active, selected_option, charges
    running = True
    while running:
        screen.fill(WHITE)

        # Рисуем сохраненные линии, если нужно
        if draw_lines:
            if mode == "field" and field_lines_surface:
                screen.blit(field_lines_surface, (0, 0))
            elif mode == "equipotential" and equipotential_lines_surface:
                screen.blit(equipotential_lines_surface, (0, 0))
            elif mode == "focus":
                # Для режима фокусировки перерисовываем каждый кадр
                focus_lines_surface.fill((0, 0, 0, 0))
                draw_focus_lines(focus_lines_surface)
                screen.blit(focus_lines_surface, (0, 0))
            elif mode == "potential_map" and potential_map_surface:
                screen.blit(potential_map_surface, (0, 0))

        # Рисуем заряды
        draw_charges()

        # Отображаем кнопки поверх всего
        draw_buttons()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # Обработка кликов на выпадающее меню
                if dropdown_rect.collidepoint(x, y):
                    dropdown_active = not dropdown_active
                elif dropdown_active:
                    for i, option in enumerate(dropdown_options):
                        option_rect = pygame.Rect(WIDTH - 150, 40 + i * 30, 140, 30)
                        if option_rect.collidepoint(x, y):
                            selected_option = i
                            dropdown_active = False
                            if selected_option == 0:
                                mode = "field"
                            elif selected_option == 1:
                                mode = "equipotential"
                            elif selected_option == 2:
                                mode = "focus"
                            elif selected_option == 3:
                                mode = "potential_map"
                # Обработка кликов на кнопку "Построить"
                elif button_build_rect.collidepoint(x, y):
                    draw_lines = True
                    if mode == "field":
                        build_field_lines()
                    elif mode == "equipotential":
                        build_equipotential_lines()
                    elif mode == "focus":
                        build_focus_lines()
                    elif mode == "potential_map":
                        build_potential_map()
                # Обработка кликов на кнопку "Сброс"
                elif button_reset_rect.collidepoint(x, y):
                    reset_simulation()
                elif y > 130 and mode != "focus":  # Игнорируем клики выше кнопок и в режиме фокусировки
                    if event.button == 1:
                        charges.append((x, y, -1))
                    elif event.button == 3:
                        charges.append((x, y, 1))

    pygame.quit()


if __name__ == "__main__":
    main()