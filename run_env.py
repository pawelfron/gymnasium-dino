import gymnasium as gym
from src.Env import DinoEnv  # assuming you save it as dino_env.py
import time

env = DinoEnv(render_mode="human")

obs, _ = env.reset()
done = False
while not done:
    action = env.action_space.sample()  # random jump or not
    obs, reward, done, truncated, info = env.step(action)
    env.render()
    time.sleep(0.01)

env.close()