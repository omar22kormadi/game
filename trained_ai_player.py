from time import time
import numpy as np
from player import Player
from config import *
import os

class TrainedAIPlayer(Player):
    def __init__(self, x, y, model=None):
        super().__init__(x, y, PLAYER2_COLOR, "Trained AI Player")
        self.model = model
        self.last_action = 0

    def _get_observation(self, falling_objects):
        ai_center = self.x + self.width // 2

        threats = []
        for obj in falling_objects:
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
            (SCREEN_WIDTH - self.x) / SCREEN_WIDTH,
            self.x / SCREEN_WIDTH,
        ]

        for threat in threats:
            observation.extend(threat)

        return np.array(observation, dtype=np.float32)

    def update(self, falling_objects):
        if self.model is None:
            return

        observation = self._get_observation(falling_objects)
        action, _states = self.model.predict(observation, deterministic=True)
        #print ai action every 3 seconds
        if time() % 3 < 0.1:
            print(f"AI Action: {action}")
        

        if action == 1:
            self.move(-1)
        elif action == 2:
            self.move(1)

        self.last_action = action

def load_trained_model():
    from stable_baselines3 import PPO

    model_path = "models/dodge_game_ppo"

    if not os.path.exists(f"{model_path}.zip"):
        print(f"Error: Trained model not found at {model_path}.zip")
        print("Please run: python train_ai.py")
        return None

    try:
        model = PPO.load(model_path)
        print("Trained AI model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
