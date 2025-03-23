from core.state_machine import StateMachine
from agents.q_learning_agent import QLearningAgent
from agents.dqn_agent import DQNAgent
from environnements.snake_env import SnakeEnv
from environnements.pong_env import PongEnv

state_machines = {}
envs = {}
agents = {}

def get_state_machine(game: str = "snake"):
    if game not in state_machines:
        state_machines[game] = StateMachine()
    return state_machines[game]

def get_env(game: str = "snake"):
    if game not in envs:
        if game.lower() == "pong":
            envs[game] = PongEnv()
        else:
            envs[game] = SnakeEnv()
    return envs[game]

def get_agent(game: str = "snake"):
    if game not in agents:
        from agents.dqn_agent import DQNAgent
        agent = DQNAgent()
        agent.initialize(get_env(game), game)
        agents[game] = agent
    return agents[game]

