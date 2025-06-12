import unittest
from unittest.mock import patch
import pygame

# Import the module to test
import game_logic

class TestGameLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize pygame for Rect functionality
        pygame.init()

    def setUp(self):
        # Ensure global obstacles list is reset before each test
        game_logic.obstacles.clear()

    @patch('game_logic.random.randint')
    def test_spawn_obstacle_fixed_gap(self, mock_randint):
        # Mock the gap position to a known value
        mock_gap = 150
        mock_randint.return_value = mock_gap

        game_logic.spawn_obstacle()
        self.assertEqual(len(game_logic.obstacles), 1)

        top, bottom, passed = game_logic.obstacles[0]
        # Top rectangle should span from y=0 to y=mock_gap
        self.assertEqual(top.topleft, (game_logic.WIDTH, 0))
        self.assertEqual(top.height, mock_gap)
        # Bottom rectangle should start just after the gap
        self.assertEqual(bottom.top, mock_gap + game_logic.gap_height)
        self.assertFalse(passed)

    def test_update_fish_position_moves_towards_mouse(self):
        # Escenario hacia arriba
        fish = pygame.Rect(0, 100, 10, 10)
        updated = game_logic.update_fish_position(fish.copy(), 50)
        delta = int((50 - 100) * 0.1)
        self.assertEqual(updated.centery, 100 + delta)

        # Escenario hacia abajo
        fish = pygame.Rect(0, 200, 10, 10)
        updated = game_logic.update_fish_position(fish.copy(), 300)
        delta = int((300 - 200) * 0.1)
        self.assertEqual(updated.centery, 200 + delta)



    def test_check_collision_false_when_no_overlap(self):
        fish = pygame.Rect(100, 100, 20, 20)
        # Place obstacle far away
        top = pygame.Rect(300, 0, 50, 50)
        bottom = pygame.Rect(300, 100, 50, 400)
        obstacles = [(top, bottom, False)]
        self.assertFalse(game_logic.check_collision(fish, obstacles))

    def test_check_collision_true_on_overlap(self):
        fish = pygame.Rect(100, 100, 20, 20)
        # Place obstacle overlapping fish
        top = pygame.Rect(90, 90, 30, 30)
        bottom = pygame.Rect(200, 200, 30, 30)
        obstacles = [(top, bottom, False)]
        self.assertTrue(game_logic.check_collision(fish, obstacles))

    def test_increment_score_no_obstacles(self):
        fish = pygame.Rect(100, 100, 20, 20)
        new_obs, score = game_logic.increment_score([], fish, 5)
        self.assertEqual(new_obs, [])
        self.assertEqual(score, 5)

    def test_increment_score_increments_and_marks_passed(self):
        fish = pygame.Rect(150, 100, 20, 20)
        # Obstacle that has just passed the fish
        top = pygame.Rect(100, 0, 50, 50)  # right=150 equal fish.left=150 => not yet passed
        bottom = pygame.Rect(100, 100, 50, 400)
        obstacles = [(top, bottom, False)]

        # First call: not yet passed
        new_obs, score = game_logic.increment_score(obstacles, fish, 0)
        self.assertEqual(score, 0)
        self.assertFalse(new_obs[0][2])

        # Move obstacle a bit further
        top.x = 90  # right=140 < fish.left=150 -> should count
        bottom.x = 90
        new_obs, score = game_logic.increment_score(new_obs, fish, score)
        self.assertEqual(score, 1)
        self.assertTrue(new_obs[0][2])

    def test_increment_score_filters_outside_screen(self):
        fish = pygame.Rect(150, 100, 20, 20)
        # Obstáculo completamente fuera de pantalla (right <= 0)
        top = pygame.Rect(-100, 0, 50, 50)
        bottom = pygame.Rect(-100, 100, 50, 400)
        obstacles = [(top, bottom, False)]

        new_obs, score = game_logic.increment_score(obstacles, fish, 0)

        # No debe quedar ningún obstáculo y no suma puntos
        self.assertEqual(new_obs, [])
        self.assertEqual(score, 0)



if __name__ == '__main__':
    unittest.main()
