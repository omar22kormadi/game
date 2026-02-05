import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from training_env import DodgeGameEnv
import os

def train_ai():
    model_dir = "models"
    model_path = os.path.join(model_dir, "dodge_game_ppo")
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    print("Creating training environment...")
    vec_env = make_vec_env(DodgeGameEnv, n_envs=4)
    
    # Check if model exists and load it
    if os.path.exists(f"{model_path}.zip"):
        print("Loading existing model to continue training...")
        model = PPO.load(model_path, env=vec_env)
        print("Existing model loaded successfully!")
    else:
        print("No existing model found. Starting fresh training...")
        model = PPO(
            "MlpPolicy",
            vec_env,
            learning_rate=1e-4,
            n_steps=1024,
            batch_size=128,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            verbose=1,
            tensorboard_log="./logs/",
        )

    total_timesteps = 500000
    print(f"Training for {total_timesteps} more timesteps...")
    model.learn(total_timesteps=total_timesteps, progress_bar=True, reset_num_timesteps=False)
    
    model.save(model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_ai()
