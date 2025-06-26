import unittest
import pygame
import os
import tempfile
import sys
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio padre al path para poder importar game.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar el código a testear
try:
    from app.main import (
        GameConfig, AssetManager, Fish, Obstacle, Button, Game,
        show_game_over, save_high_score, load_high_score,
        WIDTH, HEIGHT
    )
    print("✓ Módulo game.py importado correctamente")
except ImportError as e:
    print(f"✗ Error importando game.py: {e}")
    print("Asegúrate de que game.py esté en el directorio padre")
    sys.exit(1)


class TestGameConfig(unittest.TestCase):
    """Tests para la clase GameConfig"""
    
    def test_constants(self):
        """Test de constantes de configuración"""
        self.assertEqual(GameConfig.WIDTH, 800)
        self.assertEqual(GameConfig.HEIGHT, 600)
        self.assertEqual(GameConfig.FPS, 60)
        self.assertEqual(GameConfig.OBSTACLE_WIDTH, 80)
        self.assertEqual(GameConfig.GAP_HEIGHT, 200)
        self.assertEqual(GameConfig.INITIAL_OBSTACLE_SPEED, 4)
        self.assertEqual(GameConfig.INITIAL_OBSTACLE_INTERVAL, 1500)
        self.assertEqual(GameConfig.ROTATION_SPEED, 15)
    
    def test_colors(self):
        """Test de colores definidos"""
        self.assertEqual(GameConfig.BLUE, (0, 150, 255))
        self.assertEqual(GameConfig.GREEN, (0, 255, 100))
        self.assertEqual(GameConfig.WHITE, (255, 255, 255))
        self.assertEqual(GameConfig.BLACK, (0, 0, 0))


class TestAssetManager(unittest.TestCase):
    """Tests para la clase AssetManager"""
    
    def setUp(self):
        """Setup para cada test"""
        pygame.init()
        pygame.mixer.init()
    
    def tearDown(self):
        """Cleanup después de cada test"""
        pygame.quit()
    
    @patch('pygame.mixer.Sound')
    @patch('pygame.image.load')
    @patch('os.path.join')
    def test_load_assets_success(self, mock_join, mock_image_load, mock_sound):
        """Test carga exitosa de assets"""
        # Mock de los assets
        mock_image = Mock()
        mock_image.convert_alpha.return_value = mock_image
        mock_image_load.return_value = mock_image
        mock_join.return_value = "fake_path"
        
        # Mock de transform.scale
        with patch('pygame.transform.scale', return_value=mock_image):
            asset_manager = AssetManager()
            
            # Verificar que se cargaron los assets
            self.assertIsNotNone(asset_manager.get('fish_img'))
            self.assertIsNotNone(asset_manager.get('tubo_img'))
            self.assertIsNotNone(asset_manager.get('alga_img'))
            self.assertIsNotNone(asset_manager.get('background'))
    
    @patch('pygame.mixer.Sound', side_effect=pygame.error("Mock error"))
    @patch('pygame.image.load', side_effect=pygame.error("Mock error"))
    def test_load_assets_failure_creates_dummy(self, mock_image_load, mock_sound):
        """Test que se crean assets dummy cuando falla la carga"""
        with patch('pygame.Surface') as mock_surface:
            mock_surface_instance = Mock()
            mock_surface.return_value = mock_surface_instance
            
            asset_manager = AssetManager()
            
            # Verificar que se crearon assets dummy
            self.assertIsNotNone(asset_manager.get('fish_img'))
            self.assertIsNotNone(asset_manager.get('tubo_img'))
    
    def test_get_existing_asset(self):
        """Test obtener asset existente"""
        asset_manager = AssetManager()
        # Agregar un asset mock
        asset_manager.assets['test_asset'] = "test_value"
        
        result = asset_manager.get('test_asset')
        self.assertEqual(result, "test_value")
    
    def test_get_nonexisting_asset(self):
        """Test obtener asset inexistente"""
        asset_manager = AssetManager()
        
        result = asset_manager.get('nonexistent')
        self.assertIsNone(result)


class TestFish(unittest.TestCase):
    """Tests para la clase Fish"""
    
    def setUp(self):
        """Setup para cada test"""
        pygame.init()
        
        # Mock asset manager con Surface real
        self.mock_asset_manager = Mock()
        # Crear una Surface real para evitar problemas con mask
        mock_image = pygame.Surface((90, 90), pygame.SRCALPHA)
        mock_image.fill((255, 255, 255, 255))  # Superficie blanca
        self.mock_asset_manager.get.return_value = mock_image
        
        self.fish = Fish(self.mock_asset_manager)
    
    def tearDown(self):
        """Cleanup después de cada test"""
        pygame.quit()
    
    def test_fish_initialization(self):
        """Test inicialización del pez"""
        self.assertEqual(self.fish.angle, 0)
        self.assertFalse(self.fish.rotating)
        self.assertEqual(self.fish.rotation_speed, GameConfig.ROTATION_SPEED)
    
    def test_update_position(self):
        """Test actualización de posición"""
        initial_y = self.fish.rect.centery
        target_y = initial_y + 100
        
        self.fish.update(target_y)
        
        # La posición debería cambiar hacia el target
        self.assertNotEqual(self.fish.rect.centery, initial_y)
    
    def test_update_with_rotation(self):
        """Test actualización con rotación"""
        self.fish.start_rotation()
        initial_angle = self.fish.angle
        
        with patch('pygame.transform.rotate') as mock_rotate:
            mock_rotated = pygame.Surface((90, 90), pygame.SRCALPHA)
            mock_rotate.return_value = mock_rotated
            
            self.fish.update(300)
        
        # El ángulo debería haber cambiado
        self.assertGreater(self.fish.angle, initial_angle)
    
    def test_start_rotation(self):
        """Test iniciar rotación"""
        self.fish.start_rotation()
        self.assertTrue(self.fish.rotating)
    
    def test_reset(self):
        """Test reset del pez"""
        # Cambiar estado
        self.fish.angle = 45
        self.fish.rotating = True
        
        self.fish.reset()
        
        # Verificar que se reseteó
        self.assertEqual(self.fish.angle, 0)
        self.assertFalse(self.fish.rotating)
    
    def test_rotation_complete_cycle(self):
        """Test ciclo completo de rotación"""
        self.fish.start_rotation()
        self.fish.angle = 350
        
        with patch('pygame.transform.rotate') as mock_rotate:
            mock_rotated = pygame.Surface((90, 90), pygame.SRCALPHA)
            mock_rotate.return_value = mock_rotated
            
            self.fish.update(300)
        
        # Después de completar 360 grados, debería parar
        self.assertEqual(self.fish.angle, 0)
        self.assertFalse(self.fish.rotating)


class TestObstacle(unittest.TestCase):
    """Tests para la clase Obstacle"""
    
    def setUp(self):
        """Setup para cada test"""
        pygame.init()
        
        # Mock asset manager
        self.mock_asset_manager = Mock()
        mock_image = pygame.Surface((80, 100), pygame.SRCALPHA)
        self.mock_asset_manager.get.return_value = mock_image
        
        with patch('pygame.transform.scale', return_value=mock_image):
            self.obstacle = Obstacle(200, self.mock_asset_manager)
    
    def tearDown(self):
        """Cleanup después de cada test"""
        pygame.quit()
    
    def test_obstacle_initialization(self):
        """Test inicialización del obstáculo"""
        self.assertEqual(self.obstacle.gap_y, 200)
        self.assertFalse(self.obstacle.passed)
        self.assertEqual(self.obstacle.top_rect.x, GameConfig.WIDTH)
    
    def test_update_position(self):
        """Test actualización de posición"""
        initial_x = self.obstacle.top_rect.x
        speed = 5
        
        self.obstacle.update(speed)
        
        self.assertEqual(self.obstacle.top_rect.x, initial_x - speed)
        self.assertEqual(self.obstacle.bottom_rect.x, initial_x - speed)
    
    def test_is_off_screen(self):
        """Test verificación fuera de pantalla"""
        self.assertFalse(self.obstacle.is_off_screen())
        
        # Mover fuera de pantalla
        self.obstacle.top_rect.x = -100
        self.obstacle.bottom_rect.x = -100
        
        self.assertTrue(self.obstacle.is_off_screen())
    
    def test_check_passed(self):
        """Test verificar si el pez pasó"""
        # Mock fish
        mock_fish = Mock()
        mock_fish.rect.left = 100
        
        # Obstáculo no ha pasado
        self.obstacle.top_rect.right = 200
        result = self.obstacle.check_passed(mock_fish)
        self.assertFalse(result)
        
        # Obstáculo ha pasado
        self.obstacle.top_rect.right = 50
        result = self.obstacle.check_passed(mock_fish)
        self.assertTrue(result)
        self.assertTrue(self.obstacle.passed)
        
        # Segunda llamada no debería marcar como pasado de nuevo
        result = self.obstacle.check_passed(mock_fish)
        self.assertFalse(result)
    
    def test_check_collision(self):
        """Test verificación de colisión"""
        # Mock fish con mask
        mock_fish = Mock()
        mock_fish.rect = pygame.Rect(100, 100, 90, 90)
        mock_fish.mask.overlap.return_value = None
        
        # Sin colisión
        result = self.obstacle.check_collision(mock_fish)
        self.assertFalse(result)
        
        # Con colisión en top
        mock_fish.mask.overlap.side_effect = [True, None]
        result = self.obstacle.check_collision(mock_fish)
        self.assertTrue(result)
        
        # Con colisión en bottom
        mock_fish.mask.overlap.side_effect = [None, True]
        result = self.obstacle.check_collision(mock_fish)
        self.assertTrue(result)


class TestButton(unittest.TestCase):
    """Tests para la clase Button"""
    
    def setUp(self):
        """Setup para cada test"""
        pygame.init()
        self.button = Button(100, 100, 200, 50, "Test", 
                           GameConfig.GREEN, GameConfig.DARK_GREEN)
    
    def tearDown(self):
        """Cleanup después de cada test"""
        pygame.quit()
    
    def test_button_initialization(self):
        """Test inicialización del botón"""
        self.assertEqual(self.button.text, "Test")
        self.assertEqual(self.button.color, GameConfig.GREEN)
        self.assertEqual(self.button.current_color, GameConfig.GREEN)
    
    def test_check_hover_inside(self):
        """Test hover dentro del botón"""
        result = self.button.check_hover((150, 125))
        self.assertTrue(result)
        self.assertEqual(self.button.current_color, self.button.hover_color)
    
    def test_check_hover_outside(self):
        """Test hover fuera del botón"""
        result = self.button.check_hover((50, 50))
        self.assertFalse(result)
        self.assertEqual(self.button.current_color, self.button.color)
    
    def test_is_clicked_true(self):
        """Test click verdadero"""
        result = self.button.is_clicked((150, 125), True)
        self.assertTrue(result)
    
    def test_is_clicked_false_outside(self):
        """Test click falso por posición"""
        result = self.button.is_clicked((50, 50), True)
        self.assertFalse(result)
    
    def test_is_clicked_false_no_click(self):
        """Test click falso por no hacer click"""
        result = self.button.is_clicked((150, 125), False)
        self.assertFalse(result)
        
    def test_draw_no_font(self):
        """Si font es None, no debe dibujar nada."""
        # Dummy surface que registra blits
        class DummySurface:
            def __init__(self):
                self.blit_calls = []
            def blit(self, surf, rect):
                self.blit_calls.append((surf, rect))

        surface = DummySurface()
        btn = Button(0, 0, 100, 50, "Txt", GameConfig.GREEN, GameConfig.DARK_GREEN)
        btn.font = None
        btn.current_color = (1,2,3)

        called = {"rect": False}
        def fake_rect(*args, **kwargs):
            called["rect"] = True
        with patch('pygame.draw.rect', fake_rect):
            btn.draw(surface)

        self.assertFalse(called["rect"], "No se debe llamar a pygame.draw.rect cuando font es None")
        self.assertEqual(surface.blit_calls, [])

    def test_draw_with_font(self):
        """Con font presente, debe dibujar fondo, borde, renderizar texto y blit."""
        # Dummy surface y font
        class DummySurface:
            def __init__(self):
                self.blit_calls = []
            def blit(self, surf, rect):
                self.blit_calls.append((surf, rect))
        class DummyFont:
            def __init__(self):
                self.render_calls = []
                self._fake_surface = pygame.Surface((10, 10))
            def render(self, text, aa, color):
                self.render_calls.append((text, aa, color))
                # devolvemos la “superficie” simulada
                return self._fake_surface

        surface = DummySurface()
        font = DummyFont()
        btn = Button(10, 20, 80, 30, "Hola", GameConfig.GREEN, GameConfig.DARK_GREEN)
        btn.font = font
        btn.current_color = (9,8,7)

        rect_calls = []
        def fake_rect(surf, color, rect, *args, **kwargs):
            rect_calls.append((color, rect))
        with patch('pygame.draw.rect', fake_rect):
            btn.draw(surface)

        # 1) fondo
        self.assertEqual(rect_calls[0][0], btn.current_color)
        self.assertEqual(rect_calls[0][1], btn.rect)
        # 2) borde
        self.assertEqual(rect_calls[1][0], GameConfig.BLACK)
        self.assertEqual(rect_calls[1][1], btn.rect)

        # render de texto
        self.assertEqual(font.render_calls, [(btn.text, True, GameConfig.WHITE)])
        # blit del surface devuelto por font.render
        self.assertEqual(len(surface.blit_calls), 1)
        surf_rendered, rect_rendered = surface.blit_calls[0]
        self.assertIs(surf_rendered, font._fake_surface)
        self.assertEqual(rect_rendered.center, btn.rect.center)


class TestGame(unittest.TestCase):
    """Tests para la clase Game"""
    
    def setUp(self):
        """Setup para cada test"""
        pygame.init()
        pygame.mixer.init()
        
        # Mock pygame.display.set_mode para evitar crear ventana real
        with patch('pygame.display.set_mode'):
            with patch('pygame.display.set_caption'):
                # Mock load_high_score para evitar cargar desde archivo
                with patch.object(Game, 'load_high_score', return_value=0):
                    self.game = Game()
    
    def tearDown(self):
        """Cleanup después de cada test"""
        pygame.quit()
    
    def test_game_initialization(self):
        """Test inicialización del juego"""
        self.assertEqual(self.game.score, 0)
        self.assertTrue(self.game.game_active)
        self.assertEqual(len(self.game.obstacles), 0)
    
    def test_reset_game_state(self):
        """Test reset del estado del juego"""
        # Cambiar estado
        self.game.score = 10
        self.game.game_active = False
        self.game.obstacles = [Mock()]
        
        self.game.reset_game_state()
        
        # Verificar reset
        self.assertEqual(self.game.score, 0)
        self.assertTrue(self.game.game_active)
        self.assertEqual(len(self.game.obstacles), 0)
    
    def test_spawn_obstacle(self):
        """Test creación de obstáculo"""
        initial_count = len(self.game.obstacles)
        
        with patch('random.randint', return_value=300):
            self.game.spawn_obstacle()
        
        self.assertEqual(len(self.game.obstacles), initial_count + 1)
    
    def test_handle_score_increase(self):
        """Test manejo de aumento de puntuación"""
        # Establecer high_score inicial explícitamente
        self.game.high_score = 0
        
        # Mock de los métodos de high score
        with patch.object(self.game, 'save_high_score') as mock_save:
            self.game.score = 10
            self.game.handle_score_increase()
        
        # Verificar que se actualizó el high score
        self.assertEqual(self.game.high_score, 10)
        # Verificar que se llamó save_high_score
        mock_save.assert_called_once_with(10)
    
    def test_handle_score_increase_rotation(self):
        """Test rotación en múltiplos de 10"""
        self.game.score = 20
        self.game.high_score = 0
        
        with patch.object(self.game, 'save_high_score'):
            with patch.object(self.game.fish, 'start_rotation') as mock_rotation:
                self.game.handle_score_increase()
                mock_rotation.assert_called_once()
    
    @patch('tempfile.NamedTemporaryFile')
    def test_save_high_score(self, mock_temp):
        """Test guardar high score"""
        save_high_score(100)
        # Si no hay error, el test pasa
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_high_score_file_not_found(self, mock_open):
        """Test cargar high score cuando no existe archivo"""
        result = load_high_score()
        self.assertEqual(result, 0)
    
    def test_compatibility_functions(self):
        """Test funciones de compatibilidad"""
        # Test variables de compatibilidad
        self.assertEqual(WIDTH, GameConfig.WIDTH)
        self.assertEqual(HEIGHT, GameConfig.HEIGHT)
        
    @patch('pygame.transform.scale')
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.quit')
    def test_run_quit_on_quit_event_with_background(self, mock_quit, mock_flip, mock_event_get, mock_scale):
        """run() debe dibujar el background escalado y salir inmediatamente al recibir QUIT."""
        # Preparamos un background dummy y su versión escalada
        dummy_bg = pygame.Surface((100, 100))
        dummy_scaled = pygame.Surface((GameConfig.WIDTH, GameConfig.HEIGHT))
        mock_scale.return_value = dummy_scaled

        # Configuramos el game con mocks mínimos
        game = Game()
        game.asset_manager = Mock(get=Mock(return_value=dummy_bg))
        game.screen = Mock(blit=Mock(), fill=Mock())
        game.clock = Mock(tick=Mock(return_value=123))
        game.fish = Mock(update=Mock(), draw=Mock())
        game.obstacles = []
        game.draw_ui = Mock()

        # Simulamos evento QUIT como primer y único evento
        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]

        # Ejecutamos
        result = game.run()
        self.assertIsNone(result)

        # Verificamos que se haya intentado escalar el background al menos una vez
        mock_scale.assert_any_call(dummy_bg, (GameConfig.WIDTH, GameConfig.HEIGHT))
        # Y que luego se haya bliteado esa superficie
        game.screen.blit.assert_called_with(dummy_scaled, (0, 0))
        game.screen.fill.assert_not_called()    # no debe usarse fill()

        # Al recibir QUIT debe salir antes de update/draw y flip
        game.fish.update.assert_not_called()
        game.fish.draw.assert_not_called()
        mock_flip.assert_not_called()

        # Y debe llamar a pygame.quit()
        mock_quit.assert_called_once()

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.quit')
    def test_run_quit_on_escape_key_no_background(self, mock_quit, mock_flip, mock_event_get):
        """run() debe usar fill() cuando no hay background y salir con ESCAPE sin procesar update/draw."""
        # Configuramos el game con mocks mínimos
        game = Game()
        game.asset_manager = Mock(get=Mock(return_value=None))
        game.screen = Mock(blit=Mock(), fill=Mock())
        game.clock = Mock(tick=Mock(return_value=99))
        game.fish = Mock(update=Mock(), draw=Mock())
        game.obstacles = []
        game.draw_ui = Mock()

        # Simulamos evento KEYDOWN+ESCAPE como primer y único evento
        mock_event_get.return_value = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        ]

        # Ejecutamos
        result = game.run()
        self.assertIsNone(result)

        # Debe llenar la pantalla con el color BLUE
        game.asset_manager.get.assert_called_once_with('background')
        game.screen.fill.assert_called_once_with(GameConfig.BLUE)
        game.screen.blit.assert_not_called()      # no debe usar blit()

        # No debe procesar update/draw ni flip()
        game.fish.update.assert_not_called()
        game.fish.draw.assert_not_called()
        mock_flip.assert_not_called()

        # Y debe llamar a pygame.quit()
        mock_quit.assert_called_once()
        
    @patch('pygame.display.flip')
    @patch('pygame.event.get')
    @patch('pygame.mouse.get_pos')
    @patch('app.main.Button')
    def test_show_game_over_restart(self, mock_button_cls, mock_get_pos, mock_event_get, mock_flip):
        """show_game_over() debe devolver 'restart' al pulsar Reiniciar."""
        # Preparar mocks de botones: el primero es restart, el segundo quit
        restart_btn = Mock()
        quit_btn = Mock()
        # draw y check_hover no hacen nada
        restart_btn.draw = Mock()
        quit_btn.draw = Mock()
        restart_btn.check_hover = Mock()
        quit_btn.check_hover = Mock()
        # is_clicked devuelve True para restart y luego nunca llega a quit
        restart_btn.is_clicked = Mock(return_value=True)
        quit_btn.is_clicked = Mock(return_value=False)
        mock_button_cls.side_effect = [restart_btn, quit_btn]

        # mouse.get_pos siempre devuelve (0,0)
        mock_get_pos.return_value = (0, 0)
        # simulamos un MOUSEBUTTONDOWN con botón izquierdo
        mock_event_get.return_value = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})
        ]

        game = Game()
        game.screen = Mock(blit=Mock(), fill=Mock())
        game.score = 42
        game.clock = Mock()  # no llegará a tick porque devuelve antes

        result = game.show_game_over()
        self.assertEqual(result, "restart")

        # Compruebo que creara dos botones con las posiciones correctas
        calls = mock_button_cls.call_args_list
        # Primer llamada: Reiniciar
        x1, y1, w1, h1, txt1, *_ = calls[0][0]
        self.assertEqual(txt1, "Reiniciar")
        # Segunda llamada: Salir
        x2, y2, w2, h2, txt2, *_ = calls[1][0]
        self.assertEqual(txt2, "Salir")

        # Debe haberse dibujado overlay, texto y botones al menos dos veces
        self.assertTrue(game.screen.blit.called)
        self.assertTrue(restart_btn.draw.called)

    @patch('pygame.display.flip')
    @patch('pygame.event.get')
    @patch('pygame.mouse.get_pos')
    @patch('app.main.Button')
    def test_show_game_over_quit(self, mock_button_cls, mock_get_pos, mock_event_get, mock_flip):
        """show_game_over() debe devolver 'quit' al pulsar Salir."""
        # Preparar mocks de botones: restart y quit
        restart_btn = Mock()
        quit_btn = Mock()
        restart_btn.draw = Mock()
        quit_btn.draw = Mock()
        restart_btn.check_hover = Mock()
        quit_btn.check_hover = Mock()
        # restart nunca clicado; quit sí
        restart_btn.is_clicked = Mock(return_value=False)
        quit_btn.is_clicked = Mock(return_value=True)
        mock_button_cls.side_effect = [restart_btn, quit_btn]

        mock_get_pos.return_value = (0, 0)
        mock_event_get.return_value = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})
        ]

        game = Game()
        game.screen = Mock(blit=Mock(), fill=Mock())
        game.score = 7
        game.clock = Mock()

        result = game.show_game_over()
        self.assertEqual(result, "quit")

        # Verifico que al menos una vez comprobó is_clicked en ambos
        restart_btn.is_clicked.assert_called()
        quit_btn.is_clicked.assert_called()
        # Y que dibujó el botón de salir
        self.assertTrue(quit_btn.draw.called)



class TestGameIntegration(unittest.TestCase):
    """Tests de integración"""
    
    def setUp(self):
        """Setup para tests de integración"""
        pygame.init()
        pygame.mixer.init()
    
    def tearDown(self):
        """Cleanup después de cada test"""
        pygame.quit()
    
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_full_game_initialization(self, mock_caption, mock_display):
        """Test inicialización completa del juego"""
        with patch.object(Game, 'load_high_score', return_value=0):
            game = Game()
        
        # Verificar que todos los componentes están inicializados
        self.assertIsNotNone(game.asset_manager)
        self.assertIsNotNone(game.fish)
        self.assertIsInstance(game.obstacles, list)
        self.assertTrue(game.game_active)
    
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_obstacle_fish_interaction(self, mock_caption, mock_display):
        """Test interacción entre obstáculo y pez"""
        with patch.object(Game, 'load_high_score', return_value=0):
            game = Game()
        
        # Crear obstáculo
        with patch('random.randint', return_value=300):
            game.spawn_obstacle()
        
        obstacle = game.obstacles[0]
        
        # Test colisión
        with patch.object(obstacle, 'check_collision', return_value=True):
            game.update_obstacles(100)
            self.assertFalse(game.game_active)
    
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_score_progression(self, mock_caption, mock_display):
        """Test progresión de puntuación"""
        with patch.object(Game, 'load_high_score', return_value=0):
            game = Game()
        initial_speed = game.obstacle_speed
        
        # Simular aumento de puntuación
        game.score = 4
        game.handle_score_increase()
        
        # A los 5 puntos debería aumentar la velocidad
        game.score = 5
        game.handle_score_increase()
        
        self.assertGreater(game.obstacle_speed, initial_speed)
        
    @patch.object(Game, 'load_high_score', return_value=0)
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.display.flip')
    @patch('pygame.quit')
    @patch('pygame.event.get')
    @patch('pygame.mouse.get_pos')
    def test_run_active_flow(self, mock_get_pos, mock_event_get, mock_quit,
                             mock_flip, mock_set_caption, mock_set_mode, mock_load_hs):
        """Cuando game_active=True debe llamar update, update_obstacles, draw y flip, y luego QUIT."""
        game = Game()
        # Stubs mínimos
        game.asset_manager = Mock(get=Mock(return_value=None))
        game.screen = Mock(blit=Mock(), fill=Mock())
        game.clock = Mock(tick=Mock(return_value=50))
        game.fish = Mock(update=Mock(), draw=Mock())
        # parcheo para evitar colisiones inesperadas
        game.update_obstacles = Mock()
        game.obstacles = []  # ya no importan
        game.draw_ui = Mock()
        game.game_active = True

        # 1ª iter: evento irrelevante → ejecuta el bloque activo
        # 2ª iter: QUIT → sale
        mock_event_get.side_effect = [
            [pygame.event.Event(pygame.USEREVENT)],
            [pygame.event.Event(pygame.QUIT)]
        ]
        mock_get_pos.return_value = (0, 123)

        result = game.run()
        self.assertIsNone(result)

        # Debió llamar a fish.update con Y correcto
        game.fish.update.assert_called_once_with(123)
        # Y a update_obstacles con el dt que devuelve clock.tick
        game.update_obstacles.assert_called_once_with(50)

        # Dibujado de fish
        game.fish.draw.assert_called_once_with(game.screen)
        # UI y flip en la iteración activa
        game.draw_ui.assert_called_once()
        mock_flip.assert_called_once()

        # Finalmente, al segundo evento QUIT, hace quit()
        mock_quit.assert_called_once()

    @patch('pygame.display.flip')
    @patch('pygame.quit')
    @patch('pygame.event.get')
    @patch('pygame.mouse.get_pos')
    def test_run_game_over_restart_flow(self, mock_get_pos, mock_event_get, mock_quit, mock_flip):
        """run() debe llamar show_game_over y reset_game_state cuando game_active=False."""
        game = Game()
        game.asset_manager = Mock(get=Mock(return_value=None))
        game.screen = Mock(blit=Mock(), fill=Mock())
        game.clock = Mock(tick=Mock(return_value=30))
        game.fish = Mock(update=Mock(), draw=Mock())
        game.obstacles = []
        game.draw_ui = Mock()

        # Forzamos game over desde el inicio
        game.game_active = False
        # Parcheamos show_game_over para que primero devuelva "restart"
        with patch.object(Game, 'show_game_over', side_effect=["restart", None]) as mock_sgo:
            with patch.object(Game, 'reset_game_state') as mock_reset:
                # Eventos: ninguna entrada en el loop de eventos, luego QUIT para salir tras reiniciar
                mock_event_get.side_effect = [
                    [],  # first loop: process game_over -> restart -> reset_game_state()
                    [pygame.event.Event(pygame.QUIT)]  # second loop: exit
                ]
                mock_get_pos.return_value = (0, 0)

                result = game.run()
                self.assertIsNone(result)

                # show_game_over debe haberse llamado al menos una vez
                mock_sgo.assert_called_once()
                # reset_game_state debe haberse ejecutado
                mock_reset.assert_called_once()
                # Al final se sale con quit
                mock_quit.assert_called_once()
                # flip se llamó al menos una vez
                self.assertTrue(mock_flip.called)



def run_coverage_test():
    """Función para ejecutar tests con cobertura"""
    try:
        import coverage
        
        # Inicializar coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Ejecutar tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Detener coverage y generar reporte
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("REPORTE DE COBERTURA")
        print("="*50)
        cov.report()
        
        # Generar reporte HTML
        cov.html_report(directory='htmlcov')
        print(f"\nReporte HTML generado en: htmlcov/index.html")
        
        return result.wasSuccessful()
        
    except ImportError:
        print("Para usar coverage, instala: pip install coverage")
        # Ejecutar tests sin coverage
        unittest.main(verbosity=2)
        return True


if __name__ == '__main__':
    # Verificar si se quiere ejecutar con coverage
    if len(sys.argv) > 1 and sys.argv[1] == '--coverage':
        success = run_coverage_test()
        sys.exit(0 if success else 1)
    else:
        # Ejecutar tests normalmente
        unittest.main(verbosity=2)