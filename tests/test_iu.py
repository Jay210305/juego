# import sys, os
# import pygame
# import pytest
# import importlib

# # Asegura que la carpeta raíz esté en sys.path
# dir_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if dir_root not in sys.path:
#     sys.path.insert(0, dir_root)

# from app.main import Button, reset_game, WIDTH, HEIGHT, BLACK

# # Inicializar pygame en modo headless
# def setup_module(module):
#     pygame.display.init()
#     pygame.display.set_mode((1, 1))

# def teardown_module(module):
#     pygame.quit()


# def test_button_hover_and_click():
#     btn = Button(10, 10, 100, 50, "Test", (1,2,3), (4,5,6))
#     inside = (20, 20)
#     assert btn.check_hover(inside)
#     assert btn.current_color == btn.hover_color
#     assert btn.is_clicked(inside, True)

#     outside = (0, 0)
#     assert not btn.check_hover(outside)
#     assert btn.current_color == btn.color
#     assert not btn.is_clicked(outside, True)


# def test_button_draw(monkeypatch):
#     surface = pygame.Surface((100, 50))
#     btn = Button(0, 0, 100, 50, "X", (1,1,1), (2,2,2))
#     calls = []
#     # Monkeypatch solo pygame.draw.rect para capturar llamadas
#     monkeypatch.setattr(pygame.draw, 'rect', lambda surf, color, rect, *a, **k: calls.append((surf, color)))

#     btn.draw(surface)
#     # Debió haber llamado draw.rect con el color actual y con BLACK
#     assert any(color == btn.current_color for _, color in calls)
#     assert any(color == BLACK for _, color in calls)
