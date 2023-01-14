from collections import deque
from random import random


class ReplayMemory:

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, **args):
        self.memory.append(dict(**args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)