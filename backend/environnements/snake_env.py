import numpy as np
import random
from core.base_env import GameEnvironment


class SnakeEnv(GameEnvironment):
    """
    Environment for the Snake game.
    """
    def __init__(self, grid_size: int = 10, cell_size: int = 35) -> None:
        """
        Initialize the Snake environment.

        Args:
            grid_size (int): The size of the grid.
            cell_size (int): The size of each cell.
        """
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.num_actions = 4
        self.state_size = 2 * (self.grid_size ** 2) + 2
        self.reset()

    def reset(self) -> np.ndarray:
        """
        Reset the environment to its initial state.

        Returns:
            np.ndarray: The current state of the environment.
        """
        self.snake = [[random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)]]
        self.food = self._generate_food()
        self.done = False
        return self.get_state()

    def _generate_food(self) -> list:
        """
        Generate a new food position that is not occupied by the snake.

        Returns:
            list: The [x, y] coordinates for the food.
        """
        while True:
            food = [random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)]
            if food not in self.snake:
                return food

    def step(self, action: int):
        """
        Execute one time step in the environment.

        Args:
            action (int): Action taken by the agent (0: up, 1: down, 2: left, 3: right).

        Returns:
            tuple: A tuple (state, reward, done) where:
                - state (np.ndarray): The new state.
                - reward (float): The reward received.
                - done (bool): Whether the episode has ended.
        """
        if self.done:
            return self.get_state(), -10, True

        head = self.snake[0]
        new_head = head.copy()

        # Calculate distance before movement
        prev_distance = np.linalg.norm(np.array(head) - np.array(self.food))

        if action == 0:  # Up
            new_head[1] -= 1
        elif action == 1:  # Down
            new_head[1] += 1
        elif action == 2:  # Left
            new_head[0] -= 1
        elif action == 3:  # Right
            new_head[0] += 1

        # Check for collisions with boundaries or self
        if (new_head[0] < 0 or new_head[1] < 0 or
            new_head[0] >= self.grid_size or new_head[1] >= self.grid_size or
            new_head in self.snake):
            self.done = True
            return self.get_state(), -10, True

        self.snake.insert(0, new_head)

        # Calculate distance after movement
        new_distance = np.linalg.norm(np.array(new_head) - np.array(self.food))
        distance_reward = 0.1 if new_distance < prev_distance else -0.1

        # Check if food is eaten
        if new_head == self.food:
            reward = 20
            self.food = self._generate_food()
        else:
            self.snake.pop()
            reward = -0.1

        reward += distance_reward
        return self.get_state(), reward, self.done

    def get_state(self) -> np.ndarray:
        """
        Get the current state of the environment.

        The state consists of the snake's segments (padded with -1) followed by the food coordinates.

        Returns:
            np.ndarray: The state array.
        """
        state = [coord for segment in self.snake for coord in segment]
        max_snake_length = self.grid_size ** 2
        while len(state) < 2 * max_snake_length:
            state.append(-1)
        state += self.food
        return np.array(state)

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
            bool: True if the episode is finished, otherwise False.
        """
        return self.done

    def get_config(self) -> dict:
        """
        Get the configuration for visualization.

        Returns:
            dict: A dictionary containing the grid size and cell size.
        """
        return {
            'gridSize': self.grid_size,
            'cellSize': self.cell_size
        }
