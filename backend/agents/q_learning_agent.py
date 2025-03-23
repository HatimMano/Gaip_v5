import os
import numpy as np
from core.base_agent import BaseAgent


class QLearningAgent(BaseAgent):
    """
    Q-Learning agent implementation.
    """
    def __init__(self):
        """
        Initialize the QLearningAgent.
        """
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.inference_epsilon = 0.01
        self.filename = os.path.join("models", "q_learning_model.npy")
        self.initialized = False
        self._load_model()

    def initialize(self, env) -> None:
        """
        Initialize the agent with the environment.

        Args:
            env: The environment instance with attribute `num_actions`.
        """
        self.num_actions = env.num_actions
        self.initialized = True

    def get_action(self, state, is_inferencing: bool = False) -> int:
        """
        Choose an action based on the current state using an epsilon-greedy policy.

        Args:
            state: The current state.
            is_inferencing (bool): Whether the agent is in inference mode.

        Returns:
            int: Selected action.
        """
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.num_actions)

        epsilon = self.inference_epsilon if is_inferencing else self.epsilon
        if np.random.uniform(0, 1) < epsilon:
            return np.random.randint(0, self.num_actions)

        if np.all(self.q_table[state] == self.q_table[state][0]):
            return np.random.randint(0, self.num_actions)

        return int(np.argmax(self.q_table[state]))

    def update(self, state, action: int, reward: float, next_state) -> None:
        """
        Update the Q-table based on the transition.

        Args:
            state: Current state.
            action (int): Action taken.
            reward (float): Reward received.
            next_state: Next state.
        """
        if state not in self.q_table:
            self.q_table[state] = np.random.uniform(low=-0.01, high=0.01, size=self.num_actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = np.random.uniform(low=-0.01, high=0.01, size=self.num_actions)

        if np.all(self.q_table[next_state] == self.q_table[next_state][0]):
            self.q_table[next_state] += np.random.uniform(low=-0.01, high=0.01, size=self.num_actions)

        target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state][action] += self.alpha * (target - self.q_table[state][action])
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def _load_model(self) -> None:
        """
        Load the Q-table from file if it exists.
        """
        if os.path.exists(self.filename):
            try:
                self.q_table = np.load(self.filename, allow_pickle=True).item()
                print("✅ Loaded existing Q-table from model.npy")
            except Exception as e:
                print(f"Error loading model: {e}")
        else:
            print("No existing model found. Starting from scratch.")

    def get_model(self):
        """
        Retrieve the current Q-table.

        Returns:
            dict: The Q-table.
        """
        return self.q_table

    def save_model(self) -> None:
        """
        Save the Q-table to file.
        """
        np.save(self.filename, self.q_table)
        print(f"✅ Model saved to '{self.filename}'.")
