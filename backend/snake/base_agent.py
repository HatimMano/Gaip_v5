from abc import ABC, abstractmethod

class BaseAgent:
    def __init__(self, num_actions):
        self.num_actions = num_actions

    @abstractmethod
    def train(self, num_episodes):
        """Entraîne l'agent sur un certain nombre d'épisodes."""
        pass

    @abstractmethod
    def get_action(self, state, is_inferencing=False):
        """Sélectionne une action en fonction de l'état et de la politique d'exploration."""
        pass

    @abstractmethod
    def update(self, state, action, reward, next_state):
        """Sélectionne une action en fonction de l'état et de la politique d'exploration."""
        pass

    @abstractmethod
    def set_model(self, model):
        """Charge un modèle dans l'agent."""
        pass

    @abstractmethod
    def _load_model(self, model):
        """Charge un modèle dans l'agent."""
        pass

    @abstractmethod
    def save_model(self, filename):
        """Charge un modèle dans l'agent."""
        pass