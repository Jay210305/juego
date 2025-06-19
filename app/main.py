import pygame
import random
import sys

# Inicialización
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skibidi Pescao")
clock = pygame.time.Clock()
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

#FISH
fish_img = pygame.image.load('../assets/Doby.png').convert_alpha()

# Escalado de fish
fish_img = pygame.transform.scale(fish_img, (90, 90))
fish_rect = fish_img.get_rect(center=(100, HEIGHT // 2))
fish_mask = pygame.mask.from_surface(fish_img)

# Obstáculos
obstacles = []  # cada obstáculo será: (top_rect, bottom_rect, passed)
obstacle_width = 80
gap_height = 200
obstacle_speed = 4


def spawn_obstacle():
    gap_y = random.randint(100, HEIGHT - 100 - gap_height)
    top_rect = pygame.Rect(WIDTH, 0, obstacle_width, gap_y)
    bottom_rect = pygame.Rect(WIDTH, gap_y + gap_height, obstacle_width, HEIGHT)
    obstacles.append((top_rect, bottom_rect, False))

# Botones
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 3, border_radius=10)  # Borde

        text_surface = self.font.render(self.text, True, WHITE)
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

# Función para mostrar pantalla de Game Over
def show_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Fondo semitransparente
    screen.blit(overlay, (0, 0))

    # Crear botones
    restart_button = Button(WIDTH//2 - 150, HEIGHT//2 + 50, 140, 50, "Reiniciar", GREEN, DARK_GREEN)
    quit_button = Button(WIDTH//2 + 10, HEIGHT//2 + 50, 140, 50, "Salir", CORAL, DARK_RED)

    # Texto de Game Over
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 48)

    game_over_text = font_large.render("¡GAME OVER!", True, WHITE)
    score_text = font_medium.render(f"Puntuación final: {score}", True, WHITE)

    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//4))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//3 + 50))

    # Dibujar botones
    restart_button.draw(screen)
    quit_button.draw(screen)

    pygame.display.flip()

    # Esperar la acción del jugador
    waiting = True
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Comprobar hover en botones
        restart_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        # Comprobar clic en botones
        if restart_button.is_clicked(mouse_pos, mouse_clicked):
            return "restart"
        elif quit_button.is_clicked(mouse_pos, mouse_clicked):
            return "quit"

        restart_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

# Función para reiniciar el juego
def reset_game():
    global obstacles, spawn_timer, score, fish_rect, game_active
    global obstacle_speed, obstacle_interval
    obstacle_speed = 4
    obstacle_interval = 1500

    obstacles = []
    spawn_timer = 0
    score = 0
    fish_rect.center = (100, HEIGHT // 2)
    game_active = True

# Juego principal
def main_game():
    global obstacles, spawn_timer, score, fish_rect, game_active, obstacle_speed, obstacle_interval,fondo
    obstacle_interval = 1500  # Ahora sí se asigna como global
    high_score = load_high_score()
    fondo = pygame.image.load("../assets/fondo.jpeg")

    spawn_timer = 0
    score = 0
    game_active = True

    while True:
        #background
        fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
        #background por defecto BLUE
        screen.fill(BLUE)
        #Asignando la img como background
        screen.blit(fondo,(0,0))

        dt = clock.tick(FPS)
        mouse_clicked = False

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Movimiento del pez hacia el cursor (solo eje Y)
        if game_active:
            mouse_y = pygame.mouse.get_pos()[1]
            fish_rect.centery += (mouse_y - fish_rect.centery) * 0.1

            # Mantener al pez dentro de la pantalla
            if fish_rect.top < 0:
                fish_rect.top = 0
            if fish_rect.bottom > HEIGHT:
                fish_rect.bottom = HEIGHT

        # Dibujar pez
        screen.blit(fish_img, fish_rect)

        # Obstáculos
        if game_active:
            spawn_timer += dt
            if spawn_timer > obstacle_interval:
                # Cada 1.5 segundos
                spawn_obstacle()
                spawn_timer = 0

            new_obstacles = []
            for top, bottom, passed in obstacles:
                top.x -= obstacle_speed
                bottom.x -= obstacle_speed

                pygame.draw.rect(screen, GREEN, top)
                pygame.draw.rect(screen, CORAL, bottom)

                # Puntaje
                if not passed and top.right < fish_rect.left:
                    score += 1
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

                    passed = True

                    # Aumentar velocidad cada 5 puntos
                    if score % 5 == 0:
                        obstacle_speed += 2
                        if obstacle_interval > 500:
                            obstacle_interval -= 250  # hace que aparezcan más rápido

                if top.right > 0:
                    new_obstacles.append((top, bottom, passed))

                # Colisiones
                top_surf = pygame.Surface((top.width, top.height), pygame.SRCALPHA)
                bottom_surf = pygame.Surface((bottom.width, bottom.height), pygame.SRCALPHA)

                pygame.draw.rect(top_surf, (255, 255, 255), (0, 0, top.width, top.height))
                pygame.draw.rect(bottom_surf, (255, 255, 255), (0, 0, bottom.width, bottom.height))

                top_mask = pygame.mask.from_surface(top_surf)
                bottom_mask = pygame.mask.from_surface(bottom_surf)

                top_offset = (top.x - fish_rect.x, top.y - fish_rect.y)
                bottom_offset = (bottom.x - fish_rect.x, bottom.y - fish_rect.y)

                if (fish_mask.overlap(top_mask, top_offset) or
                        fish_mask.overlap(bottom_mask, bottom_offset)):
                    game_active = False

            obstacles = new_obstacles
        else:
            # Dibujar obstáculos sin movimiento
            for top, bottom, passed in obstacles:
                pygame.draw.rect(screen, GREEN, top)
                pygame.draw.rect(screen, CORAL, bottom)

        # Mostrar puntaje
        score_text = font.render(f"Puntos: {score}", True, WHITE)
        high_score_text = font.render(f"Máx: {high_score}", True, GRAY)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

        # Si el juego no está activo, mostrar pantalla de Game Over
        if not game_active:
            action = show_game_over(score)
            if action == "restart":
                reset_game()
            elif action == "quit":
                pygame.quit()
                return

        pygame.display.flip()
def save_high_score(score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except:
        pass

def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

# Iniciar el juego
if __name__ == "__main__":
    font = pygame.font.SysFont(None, 36)
    game_active = True
    main_game()