import torch
import torch.nn as nn
import torch.optim as optim #type: ignore
import numpy as np
import os
from core.base_agent import BaseAgent


class DQNAgent(BaseAgent):
    """
    Deep Q-Network (DQN) Agent.
    """
    def __init__(self, num_actions, state_size, learning_rate=0.001, gamma=0.99, 
                 epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        super().__init__(num_actions)

        # 🧠 Réseau de neurones DQN
        self.model = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, num_actions)
        )
        
        # Optimiseur et fonction de perte
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()

        # Hyperparamètres de l'algorithme
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Gestion du GPU si disponible
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Chargement du modèle existant (si disponible)
        self._load_model("dqn_model.pth")

    def train(self, num_episodes):

        for episode in range(num_episodes):
            state = self.env.reset()
            state = torch.FloatTensor(state).to(self.device)
            done = False
            total_reward = 0

            while not done:
                # Sélection de l'action via epsilon-greedy
                action = self.get_action(state)
                next_state, reward, done, _ = self.env.step(action)

                next_state = torch.FloatTensor(next_state).to(self.device)

                # Mise à jour du réseau (backpropagation)
                target = reward + (1 - done) * self.gamma * torch.max(self.model(next_state).detach())
                prediction = self.model(state)[action]

                loss = self.criterion(prediction, target)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                state = next_state
                total_reward += reward

            # Réduction du taux d'exploration (exploration vs exploitation)
            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

            print(f"Episode {episode + 1}/{num_episodes} - Reward: {total_reward:.2f}")

    def get_action(self, state, is_inferencing=False):
        epsilon = self.epsilon if not is_inferencing else self.epsilon_min
        if np.random.rand() < epsilon:
            return np.random.randint(0, self.num_actions)

        with torch.no_grad():
            state = state.unsqueeze(0).to(self.device)
            q_values = self.model(state)
            action = torch.argmax(q_values).item()
            return action

    def update(self, state, action, reward, next_state):
        state = torch.FloatTensor(state).to(self.device)
        next_state = torch.FloatTensor(next_state).to(self.device)
        reward = torch.FloatTensor([reward]).to(self.device)

        target = reward + self.gamma * torch.max(self.model(next_state).detach())
        prediction = self.model(state)[action]

        loss = self.criterion(prediction, target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def set_model(self, model):
        self.model.load_state_dict(model)

    def _load_model(self, filename):
        if os.path.exists(filename):
            try:
                self.model.load_state_dict(torch.load(filename))
                print(f"✅ Model loaded from '{filename}'.")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
        else:
            print(f"No existing model found at '{filename}'.")

    def save_model(self, filename):
        torch.save(self.model.state_dict(), filename)
        print(f"✅ Model saved to '{filename}'.")
