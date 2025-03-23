import os
import torch  #type: ignore
import torch.nn as nn  #type: ignore
import torch.optim as optim  #type: ignore
import numpy as np
from core.base_agent import BaseAgent


class DQNAgent(BaseAgent):
    """
    Deep Q-Network (DQN) agent implementation.
    """
    def __init__(
        self, learning_rate: float = 0.001, gamma: float = 0.99,
        epsilon: float = 1.0, epsilon_decay: float = 0.995, epsilon_min: float = 0.01
    ):
        """
        Initialize the DQNAgent.

        Args:
            learning_rate (float): Learning rate for the optimizer.
            gamma (float): Discount factor.
            epsilon (float): Initial exploration rate.
            epsilon_decay (float): Decay rate for exploration.
            epsilon_min (float): Minimum exploration rate.
        """
        super().__init__(num_actions=None)
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.initialized = False

    def initialize(self, env, game: str) -> None:
        """
        Initialize the agent with the environment and build the neural network.

        Args:
            env: The environment instance.
            game (str): Game identifier used to set the model filename.
        """
        self.env = env
        self.num_actions = env.get_num_actions()
        self.state_size = getattr(env, "state_size", len(env.get_state()))
        self.filename = os.path.join("models", f"dqn_model_{game}.pth")

        self.model = nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.num_actions)
        )

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        self.model.to(self.device)
        self._load_model()
        self.initialized = True

    def train(self, num_episodes: int) -> None:
        """
        Train the agent for a specified number of episodes.

        Args:
            num_episodes (int): Number of training episodes.
        """
        for episode in range(num_episodes):
            state = self.env.reset()
            state = torch.FloatTensor(state).to(self.device)
            done = False
            total_reward = 0

            while not done:
                action = self.get_action(state)
                next_state, reward, done, _ = self.env.step(action)
                next_state = torch.FloatTensor(next_state).to(self.device)
                target = reward + (1 - done) * self.gamma * torch.max(self.model(next_state).detach())
                prediction = self.model(state)[action]
                loss = self.criterion(prediction, target)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                state = next_state
                total_reward += reward

            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
            print(f"Episode {episode + 1}/{num_episodes} - Reward: {total_reward:.2f}")

    def get_action(self, state: torch.Tensor, is_inferencing: bool = False) -> int:
        """
        Select an action using an epsilon-greedy policy.

        Args:
            state (torch.Tensor): The current state.
            is_inferencing (bool): Use a lower epsilon value during inference.

        Returns:
            int: Selected action.
        """
        epsilon = self.epsilon if not is_inferencing else self.epsilon_min
        if np.random.rand() < epsilon:
            return np.random.randint(0, self.num_actions)

        with torch.no_grad():
            state = state.unsqueeze(0).to(self.device)
            q_values = self.model(state)
            return torch.argmax(q_values).item()

    def update(self, state, action: int, reward: float, next_state) -> None:
        """
        Update the model based on the observed transition.

        Args:
            state: Current state.
            action (int): Action taken.
            reward (float): Reward received.
            next_state: Next state.
        """
        state = torch.FloatTensor(state).to(self.device)
        next_state = torch.FloatTensor(next_state).to(self.device)
        reward = torch.FloatTensor([reward]).to(self.device)

        target = reward + self.gamma * torch.max(self.model(next_state).detach())
        prediction = self.model(state)[action]

        loss = self.criterion(prediction, target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def _load_model(self) -> None:
        """
        Load the model state from file if it exists.
        """
        if os.path.exists(self.filename):
            try:
                self.model.load_state_dict(torch.load(self.filename))
                print(f"✅ Model loaded from '{self.filename}'.")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
        else:
            print(f"No existing model found at '{self.filename}'.")

    def save_model(self) -> None:
        """
        Save the model state to file.
        """
        torch.save(self.model.state_dict(), self.filename)
        print(f"✅ Model saved to '{self.filename}'.")
