import pygame
import random

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

# Pez
fish_img = pygame.Surface((50, 30), pygame.SRCALPHA)
pygame.draw.ellipse(fish_img, WHITE, [0, 0, 50, 30])
fish_rect = fish_img.get_rect(center=(100, HEIGHT // 2))

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

# Juego
spawn_timer = 0
score = 0
font = pygame.font.SysFont(None, 36)
running = True

while running:
    screen.fill(BLUE)
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento del pez hacia el cursor (solo eje Y)
    mouse_y = pygame.mouse.get_pos()[1]
    fish_rect.centery += (mouse_y - fish_rect.centery) * 0.1

    # Dibujar pez
    screen.blit(fish_img, fish_rect)

    # Obstáculos
    spawn_timer += dt
    if spawn_timer > 1500:  # Cada 1.5 segundos
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
            passed = True

        if top.right > 0:
            new_obstacles.append((top, bottom, passed))

        # Colisiones
        if fish_rect.colliderect(top) or fish_rect.colliderect(bottom):
            print("¡Game Over!")
            running = False

    obstacles = new_obstacles

    # Mostrar puntaje
    score_text = font.render(f"Score jeje : {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()