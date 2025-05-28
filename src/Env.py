import gymnasium as gym
import numpy as np
from src.Game import Game, PlayerAction

class DinoEnv(gym.Env):
    def __init__(self, render_mode=None):
        super().__init__()

        self.render_mode = render_mode

        self.action_space = gym.spaces.Discrete(2)
        low = np.array([0, 0, 0], dtype=np.float32)
        high = np.array([200, 800, 200], dtype=np.float32)
        self.observation_space = gym.spaces.Box(low, high, dtype=np.float32)

        self.game = Game()
        self.game.running = True

        self._setup_game()

    def _setup_game(self):
        pass

    def _get_obs(self):
        return np.array([], dtype=np.float32)

    def reset(self, *, seed = None, options = None):
        super().reset(seed=seed, options=options)
        self.game = Game()
        self.game.running = True
        self._setup_game()
        return self._get_obs(), {}

    def step(self, action):
        if action == 0:
            player_action = PlayerAction.NOTHING
        elif action == 1:
            player_action = PlayerAction.JUMP
        elif action == 2:
            player_action = PlayerAction.DUCK
        self.game.update(player_action, 1 / 60)
        return self._get_obs(), 0, not self.game.running, False, {}

    def render(self):
        self.game.render()

    def close(self):
        self.game.quit()
