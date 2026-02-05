import pygame
from config import *

class Player:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)

        eye_y = self.rect.y + self.height // 3
        left_eye = pygame.Rect(
            self.rect.x + self.width // 4 - 5,
            eye_y,
            10, 10
        )
        right_eye = pygame.Rect(
            self.rect.x + 3 * self.width // 4 - 5,
            eye_y,
            10, 10
        )
        pygame.draw.rect(surface, (255, 255, 255), left_eye, border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), right_eye, border_radius=5)

        pygame.draw.circle(surface, (0, 0, 0),
                         (left_eye.centerx, left_eye.centery), 3)
        pygame.draw.circle(surface, (0, 0, 0),
                         (right_eye.centerx, right_eye.centery), 3)

class ManualPlayer(Player):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER1_COLOR, "Manual Player")

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.move(-1)
        if keys[pygame.K_RIGHT]:
            self.move(1)
