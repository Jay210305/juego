# import sys
# import os
# import pygame
# import random
# import pytest

# # Asegura que la carpeta raíz (la que contiene 'app/') esté en sys.path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Importa directamente de app.main
# from app.main import (
#     spawn_obstacle, obstacles,
#     WIDTH, HEIGHT,
#     obstacle_width, gap_height
# )

# @pytest.fixture(autouse=True)
# def init_pygame_and_reset(monkeypatch):
#     # Inicializa pygame en modo headless
#     pygame.display.init()
#     pygame.display.set_mode((1,1))
#     # Parchamos las imágenes base en app.main
#     import app.main as M
#     monkeypatch.setattr(M, 'tubo_base', pygame.Surface((10, 10)))
#     monkeypatch.setattr(M, 'alga_base', pygame.Surface((10, 10)))
#     # Limpia la lista de obstáculos antes de cada test
#     obstacles.clear()
#     yield
#     pygame.quit()

# def test_spawn_obstacle_dimensions_and_masks(monkeypatch):
#     # Forzamos gap_y = 150 para determinismo
#     monkeypatch.setattr(random, 'randint', lambda a, b: 150)
    
#     spawn_obstacle()
    
#     # Debe haberse añadido exactamente un obstáculo
#     assert len(obstacles) == 1
    
#     top_rect, bottom_rect, moved_flag, top_img, bottom_img, top_mask, bottom_mask = obstacles[0]
    
#     # Verificaciones sobre los rectángulos
#     assert top_rect.x == WIDTH
#     assert top_rect.y == 0
#     assert top_rect.width == obstacle_width
#     assert top_rect.height == 150
    
#     assert bottom_rect.x == WIDTH
#     assert bottom_rect.y == 150 + gap_height
#     assert bottom_rect.width == obstacle_width
#     expected_bottom_h = HEIGHT - 150 - gap_height
#     assert bottom_rect.height == expected_bottom_h
    
#     # Verifica que las imágenes estén escaladas correctamente
#     assert top_img.get_size() == (obstacle_width, 150)
#     assert bottom_img.get_size() == (obstacle_width, expected_bottom_h)
    
#     # Verifica que los masks sean del tipo correcto
#     assert isinstance(top_mask, pygame.mask.Mask)
#     assert isinstance(bottom_mask, pygame.mask.Mask)
