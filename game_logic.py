import pygame
import random

# Configuración global que podrías parametrizar
WIDTH = 800
HEIGHT = 600
obstacle_width = 80
gap_height = 200
obstacles = []

def spawn_obstacle():
    global obstacles
    gap_y = random.randint(100, HEIGHT - 100 - gap_height)
    top_rect = pygame.Rect(WIDTH, 0, obstacle_width, gap_y)
    bottom_rect = pygame.Rect(WIDTH, gap_y + gap_height, obstacle_width, HEIGHT)
    obstacles.append((top_rect, bottom_rect, False))

def update_fish_position(fish_rect, mouse_y):
    delta = int((mouse_y - fish_rect.centery) * 0.1)
    fish_rect.centery += delta
    return fish_rect

def check_collision(fish_rect, obstacles):
    for top, bottom, _ in obstacles:
        if fish_rect.colliderect(top) or fish_rect.colliderect(bottom):
            return True
    return False

def increment_score(obstacles, fish_rect, score):
     new_obstacles = []
     for top, bottom, passed in obstacles:
        if not passed and 0 < top.right < fish_rect.left:
             score += 1
             passed = True
        if top.right > 0:
             new_obstacles.append((top, bottom, passed))
     return new_obstacles, score
