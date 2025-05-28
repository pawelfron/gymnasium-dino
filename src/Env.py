import gymnasium as gym
import numpy as np
from src.Game import Game

TERMINATION_THRESHOLD = 200

class DinoEnv(gym.Env):
    def __init__(self, render_mode=None):
        super().__init__()

        self.render_mode = render_mode

        self.action_space = gym.spaces.Discrete(3)
        low = np.array([0, 0, 0], dtype=np.float32)
        high = np.array([200, 800, 200], dtype=np.float32)
        self.observation_space = gym.spaces.Box(low, high, dtype=np.float32)

        self.step_counter = 0

        self.game = Game()
        self.game.running = True


    def _get_obs(self):
        return np.array([], dtype=np.float32)

    def reset(self, *, seed = None, options = None):
        super().reset(seed=seed, options=options)
        self.game.setup()
        self.game.running = True
        self.step_counter = 0
        return self._get_obs(), {}

    def step(self, action):
        self.game.update(action, 1 / 60)
        self.step_counter += 1
        return self._get_obs(), 0, not self.game.running, self.step_counter >= TERMINATION_THRESHOLD, {}

    def render(self):
        self.game.render()

    def close(self):
        self.game.quit()
