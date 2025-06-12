import pygame
from game_logic import (
    spawn_obstacle,
    update_fish_position,
    check_collision,
    increment_score,
    obstacles as game_obstacles,
    WIDTH,
    HEIGHT,
)

# Inicialización
pygame.init()
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

# Juego
spawn_timer = 0
score = 0
font = pygame.font.SysFont(None, 36)
running = True

while running:
    dt = clock.tick(FPS)
    screen.fill(BLUE)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento del pez
    mouse_y = pygame.mouse.get_pos()[1]
    fish_rect = update_fish_position(fish_rect, mouse_y)

    # Dibujar pez
    screen.blit(fish_img, fish_rect)

    # Spawn de obstáculos cada 1.5 s
    spawn_timer += dt
    if spawn_timer > 1500:
        spawn_obstacle()
        spawn_timer = 0

    # Movimiento, dibujo, colisiones y puntaje
    for top, bottom, _ in list(game_obstacles):
        top.x -= 4
        bottom.x -= 4
        pygame.draw.rect(screen, GREEN, top)
        pygame.draw.rect(screen, CORAL, bottom)

    # Incrementar score y filtrar obstáculos fuera de pantalla
    game_obstacles, score = increment_score(game_obstacles, fish_rect, score)

    # Comprobar colisión
    if check_collision(fish_rect, game_obstacles):
        print("¡Game Over!")
        running = False

    # Mostrar puntaje
    score_text = font.render(f"Score jeje : {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Actualizar pantalla
    pygame.display.flip()

pygame.quit()
