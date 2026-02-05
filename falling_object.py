import pygame
import random
from config import *

class FallingObject:
    def __init__(self):
        self.size = random.randint(OBJECT_MIN_SIZE, OBJECT_MAX_SIZE)
        self.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.y = -self.size
        self.speed = random.uniform(OBJECT_MIN_SPEED, OBJECT_MAX_SPEED)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, OBJECT_COLOR, self.rect, border_radius=8)

        highlight = pygame.Rect(
            self.rect.x + self.size // 4,
            self.rect.y + self.size // 4,
            self.size // 3,
            self.size // 3
        )
        pygame.draw.rect(surface, (255, 100, 100), highlight, border_radius=4)
