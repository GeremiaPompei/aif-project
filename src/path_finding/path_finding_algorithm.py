from abc import ABC, abstractmethod
from typing import Callable

from nle.nethack import CompassDirection as directions

from src.minihack import Env


class PathFindingAlgorithm(ABC):

    NEIGHBORS_STEPS = {
        (-1, 0): directions.N,
        (1, 0): directions.S,
        (0, -1): directions.W,
        (0, 1): directions.E
    }

    NEIGHBORS_STEPS_INV = {action: diff for diff, action in NEIGHBORS_STEPS.items()}

    def __int__(self, env: Env = None):
        self.start = None
        self.trg = None
        self.env = env

    @abstractmethod
    def _init_config(self):
        pass

    @abstractmethod
    def _search(self, target_poss: list[tuple[int, int]], is_valid_move: Callable):
        pass

    def _extract_actions(self, parents_dict: dict):
        actions = []
        curr = self.trg
        while curr != self.start:
            neighbor = parents_dict[curr]
            diff_x = curr[0] - neighbor[0]
            diff_y = curr[1] - neighbor[1]
            action = PathFindingAlgorithm.NEIGHBORS_STEPS[(diff_x, diff_y)]
            actions.append(action)
            curr = neighbor
        actions.reverse()
        return actions

    def find_actions(self, target_poss: list[tuple[int, int]], is_valid_move: Callable):
        self._init_config()
        parents_dict = self._search(target_poss, is_valid_move)
        return self._extract_actions(parents_dict)