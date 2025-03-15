import numpy as np
import random

class QLearningAgent:
    def __init__(self, num_actions):
        self.num_actions = num_actions
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def get_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.num_actions)
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


    def load_model(self, filename):
        self.q_table = np.load(filename, allow_pickle=True).item()

    
    def get_model(self):
        return self.q_table
    
    def save_model(self, filename):
        np.save(filename, self.q_table)
