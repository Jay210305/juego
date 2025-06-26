import pygame
import random
import sys
import os

# Configuración de rutas relativas
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')

class GameConfig:
    """Configuración centralizada del juego"""
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    
    # Colores
    BLUE = (0, 150, 255)
    GREEN = (0, 255, 100)
    CORAL = (255, 100, 100)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (180, 180, 180)
    DARK_GREEN = (0, 200, 50)
    DARK_RED = (200, 50, 50)
    
    # Configuración de juego
    OBSTACLE_WIDTH = 80
    GAP_HEIGHT = 200
    INITIAL_OBSTACLE_SPEED = 4
    INITIAL_OBSTACLE_INTERVAL = 1500
    ROTATION_SPEED = 15

class AssetManager:
    """Maneja la carga de assets"""
    def __init__(self):
        self.assets = {}
        self.load_assets()
    
    def load_assets(self):
        """Carga todos los assets necesarios"""
        try:
            # Audio
            self.assets['celebration_sound'] = pygame.mixer.Sound(
                os.path.join(ASSETS_DIR, 'audio.wav')
            )
            
            # Imágenes
            self.assets['fish_img'] = pygame.image.load(
                os.path.join(ASSETS_DIR, 'Doby.png')
            ).convert_alpha()
            self.assets['fish_img'] = pygame.transform.scale(
                self.assets['fish_img'], (90, 90)
            )
            
            self.assets['tubo_img'] = pygame.image.load(
                os.path.join(ASSETS_DIR, 'tubo.png')
            ).convert_alpha()
            
            self.assets['alga_img'] = pygame.image.load(
                os.path.join(ASSETS_DIR, 'algas.png')
            ).convert_alpha()
            
            self.assets['background'] = pygame.image.load(
                os.path.join(ASSETS_DIR, 'fondo.jpeg')
            )
            
        except pygame.error as e:
            print(f"Error cargando assets: {e}")
            # Crear imágenes dummy si no se pueden cargar
            self.create_dummy_assets()
    
    def create_dummy_assets(self):
        """Crea assets dummy para testing"""
        self.assets['fish_img'] = pygame.Surface((90, 90))
        self.assets['fish_img'].fill(GameConfig.BLUE)
        
        self.assets['tubo_img'] = pygame.Surface((80, 100))
        self.assets['tubo_img'].fill(GameConfig.GREEN)
        
        self.assets['alga_img'] = pygame.Surface((80, 100))
        self.assets['alga_img'].fill(GameConfig.CORAL)
        
        self.assets['background'] = pygame.Surface((GameConfig.WIDTH, GameConfig.HEIGHT))
        self.assets['background'].fill(GameConfig.BLUE)
        
        # Audio dummy
        try:
            self.assets['celebration_sound'] = pygame.mixer.Sound(buffer=b'\x00\x00' * 1000)
        except:
            self.assets['celebration_sound'] = None
    
    def get(self, name):
        return self.assets.get(name)

class Fish:
    """Clase para manejar el pez/delfín"""
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        self.original_img = asset_manager.get('fish_img').copy()
        self.img = self.original_img.copy()
        self.rect = self.img.get_rect(center=(100, GameConfig.HEIGHT // 2))
        self.mask = pygame.mask.from_surface(self.img)
        
        # Variables de rotación
        self.angle = 0
        self.rotating = False
        self.rotation_speed = GameConfig.ROTATION_SPEED
    
    def update(self, mouse_y):
        """Actualiza la posición del pez"""
        self.rect.centery += (mouse_y - self.rect.centery) * 0.1
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, GameConfig.HEIGHT)
        
        # Manejar rotación
        if self.rotating:
            self.angle += self.rotation_speed
            if self.angle >= 360:
                self.angle = 0
                self.rotating = False
            self.img = pygame.transform.rotate(self.original_img, self.angle)
            self.rect = self.img.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.img)
    
    def start_rotation(self):
        """Inicia la rotación del pez"""
        self.rotating = True
    
    def reset(self):
        """Resetea el pez a su estado inicial"""
        self.img = self.original_img.copy()
        self.rect.center = (100, GameConfig.HEIGHT // 2)
        self.angle = 0
        self.rotating = False
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, screen):
        """Dibuja el pez en la pantalla"""
        screen.blit(self.img, self.rect)

class Obstacle:
    """Clase para un obstáculo individual"""
    def __init__(self, gap_y, asset_manager):
        self.gap_y = gap_y
        self.passed = False
        
        # Calcular alturas
        self.top_height = gap_y
        self.bottom_height = GameConfig.HEIGHT - gap_y - GameConfig.GAP_HEIGHT
        
        # Crear rectángulos
        self.top_rect = pygame.Rect(GameConfig.WIDTH, 0, GameConfig.OBSTACLE_WIDTH, self.top_height)
        self.bottom_rect = pygame.Rect(
            GameConfig.WIDTH, 
            gap_y + GameConfig.GAP_HEIGHT, 
            GameConfig.OBSTACLE_WIDTH, 
            self.bottom_height
        )
        
        # Escalar imágenes
        tubo_base = asset_manager.get('tubo_img')
        alga_base = asset_manager.get('alga_img')
        
        self.top_img = pygame.transform.scale(tubo_base, (GameConfig.OBSTACLE_WIDTH, self.top_height))
        self.bottom_img = pygame.transform.scale(alga_base, (GameConfig.OBSTACLE_WIDTH, self.bottom_height))
        
        # Crear máscaras
        self.top_mask = pygame.mask.from_surface(self.top_img)
        self.bottom_mask = pygame.mask.from_surface(self.bottom_img)
    
    def update(self, speed):
        """Actualiza la posición del obstáculo"""
        self.top_rect.x -= speed
        self.bottom_rect.x -= speed
    
    def draw(self, screen):
        """Dibuja el obstáculo"""
        screen.blit(self.top_img, self.top_rect)
        screen.blit(self.bottom_img, self.bottom_rect)
    
    def is_off_screen(self):
        """Verifica si el obstáculo está fuera de pantalla"""
        return self.top_rect.right < 0
    
    def check_collision(self, fish):
        """Verifica colisión con el pez"""
        offset_top = (self.top_rect.x - fish.rect.x, self.top_rect.y - fish.rect.y)
        offset_bottom = (self.bottom_rect.x - fish.rect.x, self.bottom_rect.y - fish.rect.y)
        
        return (fish.mask.overlap(self.top_mask, offset_top) or 
                fish.mask.overlap(self.bottom_mask, offset_bottom))
    
    def check_passed(self, fish):
        """Verifica si el pez pasó el obstáculo"""
        if not self.passed and self.top_rect.right < fish.rect.left:
            self.passed = True
            return True
        return False

class Button:
    """Clase para botones mejorada"""
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        
        # Inicializar fuente solo si pygame está inicializado
        if pygame.get_init():
            self.font = pygame.font.SysFont(None, 36)
        else:
            self.font = None

    def draw(self, surface):
        if self.font is None:
            return
            
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, GameConfig.BLACK, self.rect, 3, border_radius=10)
        text_surface = self.font.render(self.text, True, GameConfig.WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class Game:
    """Clase principal del juego"""
    def __init__(self):
        # Inicialización
        pygame.init()
        self.screen = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
        pygame.display.set_caption("Skibidi Delfín")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
        # Managers
        self.asset_manager = AssetManager()
        
        # Game objects
        self.fish = Fish(self.asset_manager)
        self.obstacles = []
        
        # Game state
        self.reset_game_state()
        
        # Messages
        self.messages = ["¡YEY  ERES ESPECIAL!", "¡PRO!", "¡SKIBIDI LEVEL!", "¡GOD DEL PESCAO!", "¡+10 IQ!"]
        self.current_message = ""
        self.message_timer = 0
        self.last_celebrated = 0
        self.last_high_score_celebration = 0
        
        # High score
        self.high_score = self.load_high_score()
    
    def reset_game_state(self):
        """Resetea el estado del juego"""
        self.obstacles = []
        self.spawn_timer = 0
        self.score = 0
        self.game_active = True
        self.obstacle_speed = GameConfig.INITIAL_OBSTACLE_SPEED
        self.obstacle_interval = GameConfig.INITIAL_OBSTACLE_INTERVAL
        
        # Reset fish
        self.fish.reset()
        
        # Reset messages
        self.current_message = ""
        self.message_timer = 0
        self.last_celebrated = 0
        self.last_high_score_celebration = 0
    
    def spawn_obstacle(self):
        """Crea un nuevo obstáculo"""
        gap_y = random.randint(100, GameConfig.HEIGHT - 100 - GameConfig.GAP_HEIGHT)
        obstacle = Obstacle(gap_y, self.asset_manager)
        self.obstacles.append(obstacle)
    
    def update_obstacles(self, dt):
        """Actualiza todos los obstáculos"""
        # Spawn nuevos obstáculos
        self.spawn_timer += dt
        if self.spawn_timer > self.obstacle_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0
        
        # Actualizar obstáculos existentes
        obstacles_to_keep = []
        
        for obstacle in self.obstacles:
            obstacle.update(self.obstacle_speed)
            
            # Verificar si pasó el obstáculo
            if obstacle.check_passed(self.fish):
                self.score += 1
                self.handle_score_increase()
            
            # Verificar colisión
            if obstacle.check_collision(self.fish):
                self.game_active = False
            
            # Mantener solo obstáculos en pantalla
            if not obstacle.is_off_screen():
                obstacles_to_keep.append(obstacle)
        
        self.obstacles = obstacles_to_keep
    
    def handle_score_increase(self):
        """Maneja el aumento de puntuación"""
        # Actualizar high score
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score(self.high_score)
            
            # Rotación cada 10 puntos de nuevo record
            if self.score % 10 == 0 and self.score != self.last_high_score_celebration:
                self.fish.start_rotation()
                self.last_high_score_celebration = self.score
        
        # Aumentar dificultad cada 5 puntos
        if self.score % 5 == 0:
            self.obstacle_speed += 2
            if self.obstacle_interval > 500:
                self.obstacle_interval -= 250
        
        # Celebración cada 10 puntos
        if self.score % 10 == 0 and self.score != self.last_celebrated:
            celebration_sound = self.asset_manager.get('celebration_sound')
            if celebration_sound:
                celebration_sound.play()
            self.last_celebrated = self.score
            self.message_timer = pygame.time.get_ticks()
            self.current_message = random.choice(self.messages)
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Puntuación
        score_text = self.font.render(f"Puntos: {self.score}", True, GameConfig.WHITE)
        high_score_text = self.font.render(f"MAX: {self.high_score}", True, GameConfig.GRAY)
        
        padding = 10
        box_width = max(score_text.get_width(), high_score_text.get_width()) + padding * 2
        box_height = score_text.get_height() + high_score_text.get_height() + padding * 3
        
        score_bg = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        score_bg.fill((0, 0, 0, 120))
        self.screen.blit(score_bg, (10, 10))
        self.screen.blit(score_text, (10 + padding, 10 + padding))
        self.screen.blit(high_score_text, (10 + padding, 10 + padding + score_text.get_height() + 5))
        
        # Mensaje de celebración
        if pygame.time.get_ticks() - self.message_timer < 2000 and self.current_message:
            self.draw_celebration_message()
    
    def draw_celebration_message(self):
        """Dibuja el mensaje de celebración"""
        msg_font = pygame.font.SysFont("Impact", 50, bold=False)
        msg_text = msg_font.render(self.current_message, True, GameConfig.WHITE)
        
        # Outline
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]:
            outline_text = msg_font.render(self.current_message, True, GameConfig.BLACK)
            self.screen.blit(outline_text, (GameConfig.WIDTH // 2 - msg_text.get_width() // 2 + dx, 80 + dy))
        
        # Background
        msg_bg = pygame.Surface((msg_text.get_width() + 20, msg_text.get_height() + 20), pygame.SRCALPHA)
        msg_bg.fill((0, 0, 0, 100))
        self.screen.blit(msg_bg, (GameConfig.WIDTH // 2 - msg_text.get_width() // 2 - 10, 80 - 10))
        self.screen.blit(msg_text, (GameConfig.WIDTH // 2 - msg_text.get_width() // 2, 80))
    
    def show_game_over(self):
        """Muestra la pantalla de game over"""
        overlay = pygame.Surface((GameConfig.WIDTH, GameConfig.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        restart_button = Button(
            GameConfig.WIDTH//2 - 150, GameConfig.HEIGHT//2 + 50, 
            140, 50, "Reiniciar", GameConfig.GREEN, GameConfig.DARK_GREEN
        )
        quit_button = Button(
            GameConfig.WIDTH//2 + 10, GameConfig.HEIGHT//2 + 50, 
            140, 50, "Salir", GameConfig.CORAL, GameConfig.DARK_RED
        )

        font_large = pygame.font.SysFont(None, 72)
        font_medium = pygame.font.SysFont(None, 48)

        game_over_text = font_large.render("¡GAME OVER!", True, GameConfig.WHITE)
        score_text = font_medium.render(f"Puntuación final: {self.score}", True, GameConfig.WHITE)

        self.screen.blit(game_over_text, (GameConfig.WIDTH//2 - game_over_text.get_width()//2, GameConfig.HEIGHT//4))
        self.screen.blit(score_text, (GameConfig.WIDTH//2 - score_text.get_width()//2, GameConfig.HEIGHT//3 + 50))

        restart_button.draw(self.screen)
        quit_button.draw(self.screen)
        pygame.display.flip()

        waiting = True
        while waiting:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_clicked = True

            restart_button.check_hover(mouse_pos)
            quit_button.check_hover(mouse_pos)

            if restart_button.is_clicked(mouse_pos, mouse_clicked):
                return "restart"
            elif quit_button.is_clicked(mouse_pos, mouse_clicked):
                return "quit"

            restart_button.draw(self.screen)
            quit_button.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(GameConfig.FPS)
    
    def save_high_score(self, score):
        """Guarda el high score"""
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(score))
        except:
            pass

    def load_high_score(self):
        """Carga el high score"""
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    
    def run(self):
        """Bucle principal del juego"""
        while True:
            # Fondo
            background = self.asset_manager.get('background')
            if background:
                fondo_scaled = pygame.transform.scale(background, (GameConfig.WIDTH, GameConfig.HEIGHT))
                self.screen.blit(fondo_scaled, (0, 0))
            else:
                self.screen.fill(GameConfig.BLUE)

            dt = self.clock.tick(GameConfig.FPS)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return

            if self.game_active:
                # Actualizar pez
                mouse_y = pygame.mouse.get_pos()[1]
                self.fish.update(mouse_y)
                
                # Actualizar obstáculos
                self.update_obstacles(dt)
            
            # Dibujar todo
            self.fish.draw(self.screen)
            
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            
            self.draw_ui()
            
            # Game over
            if not self.game_active:
                action = self.show_game_over()
                if action == "restart":
                    self.reset_game_state()
                elif action == "quit":
                    pygame.quit()
                    return

            pygame.display.flip()

# Funciones de compatibilidad para tests
def show_game_over(score):
    """Función de compatibilidad para tests existentes"""
    game = Game()
    game.score = score
    return game.show_game_over()

def save_high_score(score):
    """Función de compatibilidad para tests existentes"""
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except:
        pass

def load_high_score():
    """Función de compatibilidad para tests existentes"""
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

# Variables de compatibilidad para tests
WIDTH = GameConfig.WIDTH
HEIGHT = GameConfig.HEIGHT

if __name__ == "__main__":
    game = Game()
    game.run()