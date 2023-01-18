from abc import ABC, abstractmethod
from nle.nethack import CompassDirection as directions


class PathFindingAlgorithm(ABC):

    NEIGHBORS_STEPS = {
        (-1, 0): directions.N,
        (1, 0): directions.S,
        (0, -1): directions.W,
        (0, 1): directions.E
    }

    NEIGHBORS_STEPS_INV = {action: diff for diff, action in NEIGHBORS_STEPS.items()}

    def __int__(self):
        self.start = None
        self.trg = None

    @abstractmethod
    def _init_config(self):
        pass

    def _extract_actions(self, parents_dict):
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

    def find_actions(self, target_poss):
        self._init_config()
        parents_dict = self(target_poss)
        return self._extract_actions(parents_dict)