from typing import Callable
from src.minihack.env import Env
from src.minihack.symbol import Symbols
from src.path_finding.path_finding_algorithm import PathFindingAlgorithm


class AStar(PathFindingAlgorithm):

    def __init__(self, env: Env = None, heuristic: Callable = None, is_valid_move: Callable = lambda x: True):
        super(AStar, self).__init__()
        self.env = env
        self.heuristic_name = heuristic.__name__ if heuristic is not None else None
        self.heuristic = heuristic if heuristic is not None else lambda e, c, p: 0
        self._is_valid_move = is_valid_move
        if self.env is not None:
            self._init_config()

    def _f(self, x):
        return self.g[x] + self.h[x]

    def _init_config(self):
        self.start = self.env.find_first_char_pos(Symbols.HERO_CHAR)
        self.open_list: list[tuple[int, int]] = [self.start]
        self.close_list = []
        self.g = {}
        self.h = {}
        self.trg = None

    def __call__(self, targets_poss):
        self.g[self.start] = 0
        self.h[self.start] = self.heuristic(self.env, self.start, targets_poss)
        curr = self.start
        parents_dict = {self.start: None}
        while len(self.open_list) > 0:
            self.open_list.sort(key=self._f)
            curr = self.open_list.pop(0)
            if curr in targets_poss:
                break
            for kx, ky in PathFindingAlgorithm.NEIGHBORS_STEPS.keys():
                neighbor = curr[0] + kx, curr[1] + ky
                if self._is_valid_move(neighbor):
                    neighbor_curr_g = self.g[curr] + 1
                    if neighbor in self.open_list:
                        if self.g[neighbor] <= neighbor_curr_g:
                            continue
                    elif neighbor in self.close_list:
                        if self.g[neighbor] <= neighbor_curr_g:
                            continue
                        self.close_list.remove(neighbor)
                    else:
                        self.h[neighbor] = self.heuristic(self.env, neighbor, targets_poss)
                    parents_dict[neighbor] = curr
                    self.open_list.append(neighbor)
                    self.g[neighbor] = neighbor_curr_g

            self.close_list.append(curr)
        self.trg = curr
        return parents_dict

    def __str__(self):
        if self.heuristic_name is None:
            return "Dijkstra"
        return f"AStar(heuristic: {self.heuristic_name})"
