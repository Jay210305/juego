# import sys
# import os
# import pygame
# import pytest
# import importlib

# # Asegura que podemos importar app.main
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import app.main as M

# # Dummy clock para show_game_over
# class DummyClock:
#     def tick(self, fps):
#         return 0

# @pytest.fixture(autouse=True)
# def init_pygame_and_module(monkeypatch, tmp_path):
#     # Directorio temporal para archivos
#     monkeypatch.chdir(tmp_path)
    
#     # Inicializa pygame COMPLETAMENTE (esto es crucial)
#     pygame.init()  # Esto inicializa todos los módulos de pygame, incluyendo fonts
    
#     # Configurar display en modo headless
#     try:
#         pygame.display.set_mode((1, 1))
#     except pygame.error:
#         # Si no hay display disponible, usar display dummy
#         os.environ['SDL_VIDEODRIVER'] = 'dummy'
#         pygame.display.set_mode((1, 1))
    
#     # Parchea screen y clock en el módulo
#     monkeypatch.setattr(M, 'screen', pygame.Surface((M.WIDTH, M.HEIGHT)))
#     monkeypatch.setattr(M, 'clock', DummyClock())
#     monkeypatch.setattr(pygame.display, 'flip', lambda: None)
    
#     yield
    
#     # Cleanup opcional (puedes comentar si causa problemas)
#     # pygame.quit()

# # ---- Tests de save/load high score ----

# def test_save_and_load_high_score(tmp_path):
#     # Sin archivo, load debe ser 0
#     assert M.load_high_score() == 0
#     # Guardar y cargar
#     M.save_high_score(321)
#     path = tmp_path / "highscore.txt"
#     assert path.exists()
#     assert path.read_text() == "321"
#     assert M.load_high_score() == 321

# def test_load_high_score_invalid(tmp_path):
#     path = tmp_path / "highscore.txt"
#     path.write_text("notanumber")
#     assert M.load_high_score() == 0

# # Helper para eventos
# def make_mouse_event(event_type, **attrs):
#     return pygame.event.Event(event_type, **attrs)

# # ---- Tests de show_game_over ----

# def test_show_game_over_restart(monkeypatch):
#     # Contador para controlar cuántas veces se llama pygame.event.get
#     call_count = [0]
    
#     def mock_event_get():
#         call_count[0] += 1
#         if call_count[0] == 1:
#             # Primera llamada: devolver click del mouse
#             return [make_mouse_event(pygame.MOUSEBUTTONDOWN, button=1)]
#         else:
#             # Llamadas posteriores: devolver lista vacía para no entrar en loop infinito
#             return []
    
#     x = M.WIDTH//2 - 150 + 10  # Coordenadas del botón "Reiniciar"
#     y = M.HEIGHT//2 + 50 + 10
    
#     monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (x, y))
#     monkeypatch.setattr(pygame.event, 'get', mock_event_get)
    
#     result = M.show_game_over(score=0)
#     assert result == "restart"

# def test_show_game_over_quit(monkeypatch):
#     # Contador para controlar cuántas veces se llama pygame.event.get
#     call_count = [0]
    
#     def mock_event_get():
#         call_count[0] += 1
#         if call_count[0] == 1:
#             # Primera llamada: devolver click del mouse
#             return [make_mouse_event(pygame.MOUSEBUTTONDOWN, button=1)]
#         else:
#             # Llamadas posteriores: devolver lista vacía para no entrar en loop infinito
#             return []
    
#     x = M.WIDTH//2 + 10 + 10  # Coordenadas del botón "Salir"
#     y = M.HEIGHT//2 + 50 + 10
    
#     monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (x, y))
#     monkeypatch.setattr(pygame.event, 'get', mock_event_get)
    
#     result = M.show_game_over(score=0)
#     assert result == "quit"

# # Test adicional para verificar que las coordenadas son correctas
# def test_button_coordinates():
#     """Test para verificar que las coordenadas de los botones están bien calculadas"""
#     restart_x = M.WIDTH//2 - 150  # 800//2 - 150 = 250
#     restart_y = M.HEIGHT//2 + 50  # 600//2 + 50 = 350
    
#     quit_x = M.WIDTH//2 + 10     # 800//2 + 10 = 410
#     quit_y = M.HEIGHT//2 + 50    # 600//2 + 50 = 350
    
#     # Los botones tienen 140 de ancho y 50 de alto
#     # Restart button: (250, 350, 140, 50) -> área de 250-390, 350-400
#     # Quit button: (410, 350, 140, 50) -> área de 410-550, 350-400
    
#     # Verificar que nuestras coordenadas de test están dentro de los botones
#     restart_test_x = M.WIDTH//2 - 150 + 10  # 260
#     restart_test_y = M.HEIGHT//2 + 50 + 10  # 360
    
#     quit_test_x = M.WIDTH//2 + 10 + 10      # 420
#     quit_test_y = M.HEIGHT//2 + 50 + 10     # 360
    
#     assert 250 <= restart_test_x <= 390, f"Restart X coordinate {restart_test_x} is outside button area (250-390)"
#     assert 350 <= restart_test_y <= 400, f"Restart Y coordinate {restart_test_y} is outside button area (350-400)"
    
#     assert 410 <= quit_test_x <= 550, f"Quit X coordinate {quit_test_x} is outside button area (410-550)"
#     assert 350 <= quit_test_y <= 400, f"Quit Y coordinate {quit_test_y} is outside button area (350-400)"