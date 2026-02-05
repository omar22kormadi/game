import pygame
import sys
from config import *
from falling_object import FallingObject
from player import ManualPlayer
from ai_player import AIPlayer

class Game:
    def __init__(self, use_trained_ai=False, trained_model=None):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.use_trained_ai = use_trained_ai
        self.trained_model = trained_model

        if use_trained_ai:
            pygame.display.set_caption("Falling Objects - Trained AI vs Human")
        else:
            pygame.display.set_caption("Falling Objects - Heuristic AI vs Human")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.state = "menu"
        self.reset_game()

    def reset_game(self):
        self.manual_player = ManualPlayer(100, SCREEN_HEIGHT - 100)

        if self.use_trained_ai:
            from trained_ai_player import TrainedAIPlayer
            self.ai_player = TrainedAIPlayer(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, self.trained_model)
        else:
            self.ai_player = AIPlayer(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100)

        self.falling_objects = []
        self.frame_count = 0
        self.winner = None

    def spawn_object(self):
        if self.frame_count % OBJECT_SPAWN_RATE == 0:
            self.falling_objects.append(FallingObject())

    def check_collisions(self):
        for obj in self.falling_objects:
            if self.manual_player.alive and self.manual_player.rect.colliderect(obj.rect):
                self.manual_player.alive = False
                self.winner = "AI Player"
                self.state = "game_over"

            if self.ai_player.alive and self.ai_player.rect.colliderect(obj.rect):
                self.ai_player.alive = False
                self.winner = "Manual Player"
                self.state = "game_over"

    def update(self):
        if self.state != "playing":
            return

        self.frame_count += 1
        self.spawn_object()

        keys = pygame.key.get_pressed()
        self.manual_player.handle_input(keys)
        self.ai_player.update(self.falling_objects)

        for obj in self.falling_objects:
            obj.update()

        self.falling_objects = [obj for obj in self.falling_objects if not obj.is_off_screen()]

        self.check_collisions()

    def draw_menu(self):
        self.screen.fill(BACKGROUND_COLOR)

        title = self.font.render("FALLING OBJECTS", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        if self.use_trained_ai:
            subtitle = self.small_font.render("Trained Deep AI vs Human", True, (100, 200, 150))
        else:
            subtitle = self.small_font.render("Heuristic AI vs Human", True, (100, 150, 200))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle, subtitle_rect)

        instruction1 = self.small_font.render("Use LEFT/RIGHT arrows to move", True, TEXT_COLOR)
        instruction1_rect = instruction1.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(instruction1, instruction1_rect)

        instruction2 = self.small_font.render("Avoid falling objects!", True, TEXT_COLOR)
        instruction2_rect = instruction2.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(instruction2, instruction2_rect)

        start = self.small_font.render("Press SPACE to Start", True, PLAYER1_COLOR)
        start_rect = start.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(start, start_rect)

        player_demo = pygame.Rect(SCREEN_WIDTH // 2 - 100, 320, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.draw.rect(self.screen, PLAYER1_COLOR, player_demo, border_radius=10)

        ai_demo = pygame.Rect(SCREEN_WIDTH // 2 + 50, 320, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.draw.rect(self.screen, PLAYER2_COLOR, ai_demo, border_radius=10)

    def draw_game_over(self):
        self.screen.fill(BACKGROUND_COLOR)

        game_over_text = self.font.render("GAME OVER", True, TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(game_over_text, game_over_rect)

        winner_color = PLAYER2_COLOR if self.winner == "AI Player" else PLAYER1_COLOR
        winner_text = self.font.render(f"{self.winner} Wins!", True, winner_color)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(winner_text, winner_rect)

        restart = self.small_font.render("Press SPACE to Restart", True, TEXT_COLOR)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(restart, restart_rect)

        quit_text = self.small_font.render("Press ESC to Quit", True, (150, 150, 150))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(quit_text, quit_rect)

    def draw_playing(self):
        self.screen.fill(BACKGROUND_COLOR)

        for obj in self.falling_objects:
            obj.draw(self.screen)

        self.manual_player.draw(self.screen)
        self.ai_player.draw(self.screen)

        manual_label = self.small_font.render("You", True, PLAYER1_COLOR)
        self.screen.blit(manual_label, (self.manual_player.x - 10, self.manual_player.y - 30))

        ai_label = self.small_font.render("AI", True, PLAYER2_COLOR)
        self.screen.blit(ai_label, (self.ai_player.x + 10, self.ai_player.y - 30))

        objects_text = self.small_font.render(f"Objects: {len(self.falling_objects)}", True, TEXT_COLOR)
        self.screen.blit(objects_text, (10, 10))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_playing()
        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if event.key == pygame.K_SPACE:
                    if self.state == "menu":
                        self.state = "playing"
                        self.reset_game()
                    elif self.state == "game_over":
                        self.state = "menu"
                        self.reset_game()

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
