from typing import Callable
from nle.nethack import CompassDirection as directions, CompassIntercardinalDirection as inter_directions
from src.minihack.actions import ACTIONS_DICT
from src.minihack.env import Env
from src.minihack.symbol import Symbols, Symbol


class ASNode:
    def __init__(self, symbol: Symbol, pos: tuple[int, int]):
        self.symbol = symbol
        self.pos = pos
        self.h = 0
        self.g = 0

    def f(self):
        return self.g + self.h

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((*self.pos, self.symbol))

NEIGBOR_STEPS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class AStar:

    def __init__(self, env: Env, heuristic: Callable = None):
        self.env = env
        self.heuristic = heuristic

    def find(self, targets_pos):
        start = ASNode(Symbols.HERO_CHAR, self.env.find_first_char_pos(Symbols.HERO_CHAR))
        open_list: list[ASNode] = [start]
        close_list = {}
        while len(open_list) > 0:
            open_list.sort(key=lambda x: x.f())
            curr = open_list.pop(0)
            close_list[curr.pos] = curr
            if curr.pos in targets_pos:
                break

            cl = list(close_list.values())
            px, py = curr.pos
            for kx, ky in NEIGBOR_STEPS:
                kpx = kx + px
                kpy = ky + py
                symbol = Symbol.from_obs(self.env.obs, kpx, kpy)
                if symbol in Symbols.WALKABLE_SYMBOLS:
                    child = ASNode(symbol, (kpx, kpy))
                    if child not in open_list + cl:
                        child.g = curr.g + 1
                        if self.heuristic:
                            child.h = self.heuristic(self.env, child.pos, targets_pos)
                        open_list.append(child)

        actions = []

        while curr.symbol != Symbols.HERO_CHAR:
            neighbors: list[ASNode] = []

            px, py = curr.pos
            for kx, ky in NEIGBOR_STEPS:
                key = (px + kx, py + ky)
                if key in close_list:
                    neighbors.append(close_list[key])
                    del close_list[key]

            neighbors.sort(key=lambda x: x.f())
            if len(neighbors) > 0:
                best_neighbor = neighbors[0]
                action = self.action_move(best_neighbor.pos, curr.pos)
                actions.append(action)
                curr = best_neighbor
            else:
                break

        actions.sort(reverse=True)

        for action in actions:
            self.env.step(action)

            self.env.render(sleep_time=1)


    def action_move(self, curr, trg):
        diff_x = trg[0] - curr[0]
        diff_y = trg[1] - curr[1]
        if diff_x == -1 and diff_y == -1:
            return ACTIONS_DICT[inter_directions.NW]
        if diff_x == -1 and diff_y == 0:
            return ACTIONS_DICT[directions.N]
        if diff_x == -1 and diff_y == 1:
            return ACTIONS_DICT[inter_directions.NE]
        if diff_x == 0 and diff_y == -1:
            return ACTIONS_DICT[directions.W]
        if diff_x == 0 and diff_y == 1:
            return ACTIONS_DICT[directions.E]
        if diff_x == 1 and diff_y == -1:
            return ACTIONS_DICT[inter_directions.SW]
        if diff_x == 1 and diff_y == 0:
            return ACTIONS_DICT[directions.S]
        if diff_x == 1 and diff_y == 1:
            return ACTIONS_DICT[inter_directions.SE]

