import pygame
import random
import sys

# Inicialización
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skibidi Pescao")
clock = pygame.time.Clock()
FPS = 66

# Colores
BLUE = (0, 150, 255)
GREEN = (0, 255, 100)
CORAL = (255, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GREEN = (0, 200, 50)
DARK_RED = (200, 50, 50)

# Mensajes
messages = ["¡YEY  ERES ESPECIAL!", "¡PRO!", "¡SKIBIDI LEVEL!", "¡GOD DEL PESCAO!", "¡+10 IQ!"]
current_message = ""

# Audio
celebration_sound = pygame.mixer.Sound("../assets/audio.wav")

# Fish
fish_img_original = pygame.image.load('../assets/Doby.png').convert_alpha()
fish_img_original = pygame.transform.scale(fish_img_original, (90, 90))
fish_img = fish_img_original.copy()
fish_rect = fish_img.get_rect(center=(100, HEIGHT // 2))
fish_mask = pygame.mask.from_surface(fish_img)

# Obstáculos
obstacles = []
obstacle_width = 80
gap_height = 200
obstacle_speed = 4

# Variables de giro
dolphin_angle = 0
rotate_fish = False
rotation_speed = 15

# Variables para evitar múltiples giros
last_high_score_celebration = 0

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
        pygame.draw.rect(surface, BLACK, self.rect, 3, border_radius=10)
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

def show_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    restart_button = Button(WIDTH//2 - 150, HEIGHT//2 + 50, 140, 50, "Reiniciar", GREEN, DARK_GREEN)
    quit_button = Button(WIDTH//2 + 10, HEIGHT//2 + 50, 140, 50, "Salir", CORAL, DARK_RED)

    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 48)

    game_over_text = font_large.render("¡GAME OVER!", True, WHITE)
    score_text = font_medium.render(f"Puntuación final: {score}", True, WHITE)

    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//4))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//3 + 50))

    restart_button.draw(screen)
    quit_button.draw(screen)
    pygame.display.flip()

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

        restart_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        if restart_button.is_clicked(mouse_pos, mouse_clicked):
            return "restart"
        elif quit_button.is_clicked(mouse_pos, mouse_clicked):
            return "quit"

        restart_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

def reset_game():
    global obstacles, spawn_timer, score, fish_rect, game_active
    global obstacle_speed, obstacle_interval, last_celebrated, message_timer, current_message
    global dolphin_angle, rotate_fish, last_high_score_celebration, fish_img
    obstacle_speed = 4
    obstacle_interval = 1500
    obstacles = []
    spawn_timer = 0
    score = 0
    fish_rect.center = (100, HEIGHT // 2)
    game_active = True
    last_celebrated = 0
    message_timer = 0
    current_message = ""
    dolphin_angle = 0
    rotate_fish = False
    last_high_score_celebration = 0
    fish_img = fish_img_original.copy()

def main_game():
    global obstacles, spawn_timer, score, fish_rect, game_active
    global obstacle_speed, obstacle_interval, fondo, last_celebrated, message_timer, current_message
    global dolphin_angle, rotate_fish, fish_img, last_high_score_celebration

    obstacle_interval = 1500
    high_score = load_high_score()
    fondo = pygame.image.load("../assets/fondo.jpeg")

    spawn_timer = 0
    score = 0
    game_active = True
    last_celebrated = 0
    message_timer = 0
    current_message = ""

    while True:
        fondo_scaled = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
        screen.fill(BLUE)
        screen.blit(fondo_scaled, (0, 0))

        dt = clock.tick(FPS)
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        if game_active:
            mouse_y = pygame.mouse.get_pos()[1]
            fish_rect.centery += (mouse_y - fish_rect.centery) * 0.1
            fish_rect.top = max(fish_rect.top, 0)
            fish_rect.bottom = min(fish_rect.bottom, HEIGHT)

        # Rotación si está activa
        if rotate_fish:
            dolphin_angle += rotation_speed
            if dolphin_angle >= 360:
                dolphin_angle = 0
                rotate_fish = False
            fish_img = pygame.transform.rotate(fish_img_original, dolphin_angle)
            fish_rect = fish_img.get_rect(center=fish_rect.center)

        screen.blit(fish_img, fish_rect)

        if game_active:
            spawn_timer += dt
            if spawn_timer > obstacle_interval:
                spawn_obstacle()
                spawn_timer = 0

            new_obstacles = []
            for top, bottom, passed in obstacles:
                top.x -= obstacle_speed
                bottom.x -= obstacle_speed
                pygame.draw.rect(screen, GREEN, top)
                pygame.draw.rect(screen, CORAL, bottom)

                if not passed and top.right < fish_rect.left:
                    score += 1
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                        if score % 10 == 0 and score != last_high_score_celebration:
                            rotate_fish = True
                            last_high_score_celebration = score

                    passed = True

                    if score % 5 == 0:
                        obstacle_speed += 2
                        if obstacle_interval > 500:
                            obstacle_interval -= 250

                    if score % 10 == 0 and score != last_celebrated:
                        celebration_sound.play()
                        last_celebrated = score
                        message_timer = pygame.time.get_ticks()
                        current_message = random.choice(messages)

                if top.right > 0:
                    new_obstacles.append((top, bottom, passed))

                top_surf = pygame.Surface((top.width, top.height), pygame.SRCALPHA)
                bottom_surf = pygame.Surface((bottom.width, bottom.height), pygame.SRCALPHA)
                pygame.draw.rect(top_surf, (255, 255, 255), (0, 0, top.width, top.height))
                pygame.draw.rect(bottom_surf, (255, 255, 255), (0, 0, bottom.width, bottom.height))
                top_mask = pygame.mask.from_surface(top_surf)
                bottom_mask = pygame.mask.from_surface(bottom_surf)
                if (fish_mask.overlap(top_mask, (top.x - fish_rect.x, top.y - fish_rect.y)) or
                    fish_mask.overlap(bottom_mask, (bottom.x - fish_rect.x, bottom.y - fish_rect.y))):
                    game_active = False

            obstacles = new_obstacles
        else:
            for top, bottom, passed in obstacles:
                pygame.draw.rect(screen, GREEN, top)
                pygame.draw.rect(screen, CORAL, bottom)

        score_text = font.render(f"Puntos: {score}", True, WHITE)
        high_score_text = font.render(f"MAX: {high_score}", True, GRAY)

        padding = 10
        box_width = max(score_text.get_width(), high_score_text.get_width()) + padding * 2
        box_height = score_text.get_height() + high_score_text.get_height() + padding * 3

        score_bg = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        score_bg.fill((0, 0, 0, 120))
        screen.blit(score_bg, (10, 10))
        screen.blit(score_text, (10 + padding, 10 + padding))
        screen.blit(high_score_text, (10 + padding, 10 + padding + score_text.get_height() + 5))

        if pygame.time.get_ticks() - message_timer < 2000 and current_message:
            msg_font = pygame.font.SysFont("Impact", 50, bold=False)
            msg_text = msg_font.render(current_message, True, WHITE)
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]:
                outline_text = msg_font.render(current_message, True, BLACK)
                screen.blit(outline_text, (WIDTH // 2 - msg_text.get_width() // 2 + dx,
                                           80 + dy))
            msg_bg = pygame.Surface((msg_text.get_width() + 20, msg_text.get_height() + 20), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 100))
            screen.blit(msg_bg, (WIDTH // 2 - msg_text.get_width() // 2 - 10, 80 - 10))
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 80))

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

if __name__ == "__main__":
    font = pygame.font.SysFont(None, 36)
    game_active = True
    main_game()