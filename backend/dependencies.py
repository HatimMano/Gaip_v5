from core.state_machine import StateMachine
from agents.q_learning_agent import QLearningAgent
from agents.dqn_agent import DQNAgent
from environnements.snake_env import SnakeEnv
from environnements.pong_env import PongEnv
from environnements.tango_env import TangoEnv
from agents.gnn_agent import GNNAgent

state_machines = {}
envs = {}
agents = {}

def get_state_machine(game: str = "snake") -> StateMachine:
    """
    Retrieve the state machine associated with the given game.
    
    Args:
        game (str): The game identifier (default "snake").
    
    Returns:
        StateMachine: The state machine instance for the game.
    """
    key = game.lower()
    if key not in state_machines:
        state_machines[key] = StateMachine()
    return state_machines[key]

def get_env(game: str = "snake"):
    """
    Retrieve the environment instance for the given game.
    
    Args:
        game (str): The game identifier (default "snake").
    
    Returns:
        Environment: An instance of the appropriate environment.
    """
    key = game.lower()
    if key not in envs:
        if key == "pong":
            envs[key] = PongEnv()
        elif key == "tango":
            envs[key] = TangoEnv(
                grid_size=6,
                constraints={
                    "equal_pairs": [],
                    "diff_pairs": []
                }
            )
        else:
            envs[key] = SnakeEnv()
    return envs[key]

def get_agent(game: str = "snake"):
    """
    Retrieve the agent associated with the given game.
    
    By default, a DQNAgent is used. For Tango, you might in the future switch to a GNNAgent.
    
    Args:
        game (str): The game identifier (default "snake").
    
    Returns:
        Agent: An initialized agent for the game.
    """
    key = game.lower()
    if key not in agents:
        if key == "tango":
            agent = GNNAgent()
        else:
            agent = DQNAgent()
        agent.initialize(get_env(game), game)
        agents[key] = agent
    return agents[key]
