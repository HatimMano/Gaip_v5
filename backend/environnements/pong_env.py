import numpy as np
import random
from core.base_env import GameEnvironment


class PongEnv(GameEnvironment):
    """
    Environment for the Pong game.
    """
    def __init__(self, width: int = 400, height: int = 400, paddle_height: int = 60) -> None:
        """
        Initialize the Pong environment.

        Args:
            width (int): Width of the game area.
            height (int): Height of the game area.
            paddle_height (int): Height of the paddle.
        """
        self.width = width
        self.height = height
        self.paddle_height = paddle_height
        self.num_actions = 3  
        self.state_size = 6
        self.reset()

    def reset(self) -> np.ndarray:
        """
        Reset the environment to its initial state.

        Returns:
            np.ndarray: The normalized state of the environment.
        """
        self.paddle_y = self.height // 2
        self.opponent_y = self.height // 2
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_vx = random.choice([-4, 4])
        self.ball_vy = random.choice([-3, 3])
        self.done = False
        self.score = 0
        return self.get_state()

    def step(self, action: int):
        """
        Execute one time step in the environment.

        Args:
            action (int): Action taken by the agent (0: no movement, 1: move up, 2: move down).

        Returns:
            tuple: A tuple (state, reward, done) where:
                - state (np.ndarray): The new state.
                - reward (float): The reward received.
                - done (bool): Whether the episode has ended.
        """
        if self.done:
            return self.get_state(), -10, True

        if action == 1:
            self.paddle_y = max(0, self.paddle_y - 6)
        elif action == 2:
            self.paddle_y = min(self.height - self.paddle_height, self.paddle_y + 6)

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        if self.ball_y <= 0 or self.ball_y >= self.height:
            self.ball_vy = -self.ball_vy

        if (self.ball_x <= 20 and 
            self.paddle_y <= self.ball_y <= self.paddle_y + self.paddle_height):
            self.ball_vx = -self.ball_vx
            self.score += 1
            reward = 10
        else:
            reward = -0.1

        if (self.ball_x >= self.width - 20 and 
            self.opponent_y <= self.ball_y <= self.opponent_y + self.paddle_height):
            self.ball_vx = -self.ball_vx

        if self.ball_x < 0 or self.ball_x > self.width:
            self.done = True
            reward = -10

        if self.opponent_y + self.paddle_height // 2 < self.ball_y:
            self.opponent_y += 4
        elif self.opponent_y + self.paddle_height // 2 > self.ball_y:
            self.opponent_y -= 4

        return self.get_state(), reward, self.done

    def get_state(self) -> np.ndarray:
        """
        Get the normalized state of the environment.

        Returns:
            np.ndarray: Array representing normalized positions and velocities.
        """
        return np.array([
            self.paddle_y / self.height,
            self.opponent_y / self.height,
            self.ball_x / self.width,
            self.ball_y / self.height,
            self.ball_vx / 4,
            self.ball_vy / 3
        ])

    def get_num_actions(self) -> int:
        """
        Get the number of available actions.

        Returns:
            int: Number of actions.
        """
        return self.num_actions

    def is_done(self) -> bool:
        """
        Check if the episode has ended.

        Returns:
            bool: True if done, otherwise False.
        """
        return self.done
