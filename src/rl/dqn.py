import math
import random

import torch
from torch import nn, Tensor
from torch.functional import F

from src.minihack.actions import ACTIONS

EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000


class DQN(nn.Module):

    def __init__(self):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(2, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(512, 16)
        self.fc2 = nn.Linear(16, 84)
        self.fc3 = nn.Linear(84, len(ACTIONS))
        self.steps_done = 0

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def select_action(self, state):
        sample = random.random()
        eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * self.steps_done / EPS_DECAY)
        self.steps_done += 1
        if sample > eps_threshold:
            with torch.no_grad():
                return self(state).argmax(1)[0]
        else:
            return torch.tensor(random.sample(range(len(ACTIONS)), 1)[0])
