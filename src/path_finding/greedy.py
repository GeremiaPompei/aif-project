from typing import Callable
from src.minihack.symbol import Symbols
from src.path_finding.path_finding_algorithm import PathFindingAlgorithm


class Greedy(PathFindingAlgorithm):

    def __init__(self, heuristic: Callable):
        super(Greedy, self).__init__()
        self.heuristic_name = heuristic.__name__ if heuristic is not None else None
        self.heuristic = heuristic if heuristic is not None else lambda e, c, p: 0

    def _init_config(self):
        self.start = self.env.find_first_char_pos(Symbols.HERO_CHAR)
        self.open_list: list[tuple[int, int]] = [self.start]
        self.h = {}
        self.trg = None

    def _search(self, targets_poss: list[tuple[int, int]], is_valid_move: Callable):
        curr = self.start
        self.h[self.start] = 0
        parents_dict = {self.start: None}
        while len(self.open_list) > 0:
            self.open_list.sort(key=lambda x: self.h[x])
            curr = self.open_list.pop(0)
            if curr in targets_poss:
                break
            for kx, ky in PathFindingAlgorithm.NEIGHBORS_STEPS.keys():
                neighbor = curr[0] + kx, curr[1] + ky
                if is_valid_move(neighbor):
                    if neighbor in parents_dict:
                        continue
                    else:
                        self.h[neighbor] = self.heuristic(self.env, neighbor, targets_poss)
                        parents_dict[neighbor] = curr
                        self.open_list.append(neighbor)
        self.trg = curr
        return parents_dict

    def __str__(self):
        return "Greedy"
