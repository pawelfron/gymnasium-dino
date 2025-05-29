import gymnasium as gym
import numpy as np
from src.Game import Game

TERMINATION_THRESHOLD = 2000

class DinoEnv(gym.Env):
    def __init__(self, render_mode=None):
        super().__init__()

        self.render_mode = render_mode

        self.action_space = gym.spaces.Discrete(3)
        # position, velocity, player height, game speed, x, y, width, height
        low = np.array([260, -740, 30, 400, 100, 100, 320, 17, 35], dtype=np.float32)
        high = np.array([370, 700, 47, 1000, 1300, 1300, 375, 75, 50], dtype=np.float32)
        self.observation_space = gym.spaces.Box(low, high, dtype=np.float32)

        self.step_counter = 0

        self.game = Game()
        self.game.running = True

    def _get_obs(self):
        state = self.game.pool()
        return np.array(state, dtype=np.float32)

    def reset(self, *, seed = None, options = None):
        super().reset(seed=seed, options=options)
        self.game.setup()
        self.game.running = True
        self.step_counter = 0
        return self._get_obs(), {}

    def step(self, action):
        self.game.update(action, 1 / 60)
        self.step_counter += 1

        terminated = not self.game.running
        truncated = self.step_counter >= TERMINATION_THRESHOLD

        reward = 1
        if terminated:
            reward = -100

        return self._get_obs(), reward, terminated, truncated, {}

    def render(self):
        self.game.render()

    def close(self):
        self.game.quit()
