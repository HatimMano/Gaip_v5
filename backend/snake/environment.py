import numpy as np
import random

class SnakeEnv:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.reset()

    def reset(self):
        self.snake = [[random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)]]
        self.food = self._generate_food()
        self.done = False
        return self.get_state()

    def _generate_food(self):
        while True:
            food = [random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)]
            if food not in self.snake:
                return food

    def step(self, action):
        if self.done:
            return self.get_state(), -10, True

        head = self.snake[0]
        new_head = head[:]

        if action == 0:  # Up
            new_head[1] -= 1
        elif action == 1:  # Down
            new_head[1] += 1
        elif action == 2:  # Left
            new_head[0] -= 1
        elif action == 3:  # Right
            new_head[0] += 1

        # Check for collision with walls or itself
        if (new_head[0] < 0 or new_head[1] < 0 or
            new_head[0] >= self.grid_size or new_head[1] >= self.grid_size or
            new_head in self.snake):
            self.done = True
            return self.get_state(), -10, True

        self.snake.insert(0, new_head)

        # Eating food
        if new_head == self.food:
            reward = 20
            self.food = self._generate_food()
        else:
            self.snake.pop()
            reward = -0.1

        return self.get_state(), reward, self.done

    def get_state(self):
        return [coord for segment in self.snake for coord in segment] + self.food

    def is_done(self):
        return self.done
