from enum import Enum

class State(Enum):
    IDLE = "idle"
    TRAINING = "training"
    INFERENCING = "inferencing"
    PAUSED = "paused"


class StateMachine:
    def __init__(self):
        self.state = State.IDLE
        self.current_episode = 0
        self.max_episodes = 100
        self.total_reward = 0
        self.num_episodes_completed = 0
        self.current_reward = 0
        self.speed = 0.5  # 50 ms → 20 FPS

    def set_state(self, new_state):
        if self.is_valid_transition(new_state):
            self.state = new_state
            print(f"✅ State changed to {new_state}")
        else:
            raise ValueError(f"🚨 Invalid state transition from {self.state} to {new_state}")

    def is_valid_transition(self, new_state):
        valid_transitions = {
            State.IDLE: [State.TRAINING, State.INFERENCING, State.IDLE],
            State.TRAINING: [State.PAUSED, State.IDLE],
            State.INFERENCING: [State.PAUSED, State.IDLE],
            State.PAUSED: [State.TRAINING, State.INFERENCING, State.IDLE, State.PAUSED]
        }
        return new_state in valid_transitions[self.state]

    def reset(self):
        self.current_episode = 0
        self.total_reward = 0
        self.num_episodes_completed = 0
        self.current_reward = 0
