import numpy as np
import random
import os
from core.base_agent import BaseAgent


class QLearningAgent(BaseAgent):
    def __init__(self, num_actions):
        self.num_actions = num_actions
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.inference_epsilon = 0.01
        self._load_model()

    def get_action(self, state, is_inferencing=False):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.num_actions)
        
        # If inference : exploitation
        epsilon = self.inference_epsilon if is_inferencing else self.epsilon
        
        if np.random.uniform(0, 1) < epsilon:
            return np.random.randint(0, self.num_actions)
        
        return np.argmax(self.q_table[state])

    def update(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.num_actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(self.num_actions)

        target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state][action] += self.alpha * (target - self.q_table[state][action])

        # Reduce exploration over time
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)


    def _load_model(self):
        if os.path.exists("model.npy"):
            try:
                self.q_table = np.load("model.npy", allow_pickle=True).item()
                print("✅ Loaded existing Q-table from model.npy")
            except Exception as e:
                print(f"Error loading model: {e}")
        else:
            print("No existing model found. Starting from scratch.")

    
    def get_model(self):
        return self.q_table
    
    def save_model(self, filename):
        np.save(filename, self.q_table)
