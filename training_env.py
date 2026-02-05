import gymnasium as gym
from gymnasium import spaces
import numpy as np
from config import *
from falling_object import FallingObject

class DodgeGameEnv(gym.Env):
    metadata = {"render_modes": []}
    
    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(12,),
            dtype=np.float32
        )
        
        self.ai_x = SCREEN_WIDTH // 2
        self.falling_objects = []
        self.frame_count = 0
        self.steps = 0
        self.max_steps = 10000
        self.game_over = False
        self.collision_count = 0
        self.last_dodge_reward = 0
    
    def reset(self, seed=None):
        super().reset(seed=seed)
        self.ai_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.falling_objects = []
        self.frame_count = 0
        self.steps = 0
        self.game_over = False
        self.collision_count = 0
        self.last_dodge_reward = 0
        observation = self._get_observation()
        return observation, {}
    
    def _get_observation(self):
        ai_center = self.ai_x + PLAYER_WIDTH // 2
        threats = []
        
        for obj in self.falling_objects:
            if obj.y < SCREEN_HEIGHT * 0.6:
                obj_center = obj.x + obj.size // 2
                horizontal_distance = (obj_center - ai_center) / SCREEN_WIDTH
                vertical_distance = (SCREEN_HEIGHT - obj.y) / SCREEN_HEIGHT
                threats.append([horizontal_distance, vertical_distance, obj.speed / OBJECT_MAX_SPEED])
        
        threats.sort(key=lambda t: t[1])
        threats = threats[:3]
        
        while len(threats) < 3:
            threats.append([0, 1, 0])
        
        observation = [
            ai_center / SCREEN_WIDTH,
            (SCREEN_WIDTH - self.ai_x) / SCREEN_WIDTH,
            self.ai_x / SCREEN_WIDTH,
        ]
        
        for threat in threats:
            observation.extend(threat)
        
        return np.array(observation, dtype=np.float32)
    
    def _spawn_objects(self):
        self.frame_count += 1
        if self.steps < 1000:
            spawn_rate = 60
        elif self.steps < 3000:
            spawn_rate = 50
        else:
            spawn_rate = 40
        
        if self.frame_count % spawn_rate == 0 and len(self.falling_objects) < 15:
            self.falling_objects.append(FallingObject())
    
    def _check_collision(self):
        ai_rect = (self.ai_x, SCREEN_HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        
        for obj in self.falling_objects:
            if (ai_rect[0] < obj.x + obj.size and
                ai_rect[0] + ai_rect[2] > obj.x and
                ai_rect[1] < obj.y + obj.size and
                ai_rect[1] + ai_rect[3] > obj.y):
                return True
        return False
    
    def _calculate_near_miss_reward(self):
        ai_rect = (self.ai_x, SCREEN_HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        near_miss_reward = 0.0
        for obj in self.falling_objects:
            if SCREEN_HEIGHT - 120 < obj.y < SCREEN_HEIGHT - 40:
                horizontal_dist = abs((self.ai_x + PLAYER_WIDTH//2) - (obj.x + obj.size//2))
                if horizontal_dist < 80:
                    near_miss_reward += 0.4
        return near_miss_reward

    
    def step(self, action):
        if self.game_over:
            return self._get_observation(), 0.0, True, False, {}

        self.steps += 1

        if action == 1:
            self.ai_x = max(0, self.ai_x - PLAYER_SPEED * 2)
        elif action == 2:
            self.ai_x = min(SCREEN_WIDTH - PLAYER_WIDTH, self.ai_x + PLAYER_SPEED * 2)

        self._spawn_objects()
        for obj in self.falling_objects:
            obj.update()
        self.falling_objects = [obj for obj in self.falling_objects if not obj.is_off_screen()]

        collision = self._check_collision()
        observation = self._get_observation()

        reward = 0.0

        reward += 0.05

        near_miss = self._calculate_near_miss_reward()
        reward += near_miss * 1.5  

        if self.ai_x < 30 or self.ai_x > SCREEN_WIDTH - PLAYER_WIDTH - 30:
            reward -= 0.05

        if collision:
            reward -= 3.0
            self.game_over = True
            self.collision_count += 1

        if self.steps >= self.max_steps:
            self.game_over = True
            reward += 1.0  

        terminated = self.game_over
        truncated = self.steps >= self.max_steps

        return observation, reward, terminated, truncated, {}

    def render(self):
        pass
    
    def close(self):
        pass
