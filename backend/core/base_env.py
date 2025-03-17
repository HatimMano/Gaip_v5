from abc import ABC, abstractmethod

class GameEnvironment(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def step(self, action):
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def is_done(self):
        pass
