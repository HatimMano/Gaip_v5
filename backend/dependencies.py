
from core.state_machine import StateMachine
from snake.snake_env import SnakeEnv
from snake.q_learning_agent import QLearningAgent

# === Créer une instance unique globale ===
state_machine = StateMachine()
env = SnakeEnv()
agent = QLearningAgent(4)

# === Fonctions d'injection de dépendances ===
def get_state_machine():
    return state_machine

def get_env():
    return env

def get_agent():
    return agent
