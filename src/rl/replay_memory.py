from collections import deque
from random import sample


class ReplayMemory:

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, **args):
        self.memory.append(dict(**args))

    def sample(self, batch_size):
        return sample(self.memory, batch_size)