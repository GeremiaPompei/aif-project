from enum import Enum
from typing import Callable
from nle.nethack import CompassDirection as directions, CompassIntercardinalDirection as inter_directions, \
    Command as cmd
from src.minihack.actions import ACTIONS_DICT
from src.minihack.env import Env
from src.minihack.symbol import Symbols, Symbol


class TARGET_TYPES(Enum):
    KEY = 1
    UNEXPLORED_CORRIDOR = 2
    UNEXPLORED_FLOOR = 3
    STAIRS_DOWN = 4
    UNEXPLORED_FLOOR_CLOSE = 5


NEIGHBORS_STEPS = {
    (-1, 0): directions.N,
    (1, 0): directions.S,
    (0, -1): directions.W,
    (0, 1): directions.E
}

NEIGHBORS_STEPS_INV = {action: diff for diff, action in NEIGHBORS_STEPS.items()}


class AStar:

    def __init__(self, env: Env, heuristic: Callable = None):
        self.env = env
        self.heuristic = heuristic if heuristic is not None else lambda e, c, p: 0
        self._init_config()
        self.visited_corridors = set()
        self.unable_pos = set()

    def _init_config(self):
        self.start = self.env.find_first_char_pos(Symbols.HERO_CHAR)
        self.open_list: list[tuple[int, int]] = [self.start]
        self.close_list = []
        self.g = {}
        self.h = {}
        self.trg = None
        self.targets_poss = []

    def _f(self, x):
        return self.g[x] + self.h[x]

    def find(self):
        self._init_config()
        self._find_targets()
        self._astar()

        ######
        for x in range(self.env.shape[0]):
            for y in range(self.env.shape[1]):
                k = (x, y)
                if k in self.close_list:
                    print(str(int(self._f(k))).rjust(2, ' '), end='')
                else:
                    print('  ', end='')
            print()
        ######
        actions = self._extract_actions()

        total_steps = 0
        for action in actions:
            curr = self.env.find_first_char_pos()
            next_step_diff = NEIGHBORS_STEPS_INV[action]
            next_step = (curr[0] + next_step_diff[0], curr[1] + next_step_diff[1])
            next_step_symbol = Symbol.from_obs(self.env.obs, next_step[0], next_step[1])
            if next_step_symbol in Symbols.DOOR_CLOSE_CHARS:
                self.env.step(cmd.APPLY)
                total_steps += 1
            self.env.step(action, next_step_symbol)
            total_steps += 1
            next_step_symbol_updated = Symbol.from_obs(self.env.obs, next_step[0], next_step[1])
            if next_step_symbol_updated in Symbols.DOOR_CLOSE_CHARS \
                    or (
                    next_step_symbol_updated not in Symbols.DOOR_OPEN_CHARS and
                    self.env.find_first_char_pos() != next_step
            ):
                self.unable_pos.add(next_step)
            if self.env.over_hero_symbol in Symbols.CORRIDOR_CHARS:
                self.visited_corridors.add(self.env.find_first_char_pos(Symbols.HERO_CHAR))

            # TODO
            self.env.render(sleep_time=0.2)

        return total_steps

    def _valid_discover_floor(self, pos):
        for kx, ky in NEIGHBORS_STEPS.keys():
            if Symbol.from_obs(self.env.obs, pos[0] + kx, pos[1] + ky) == Symbols.OBSCURE_CHAR:
                return True
        return False

    def _check_terget(self, pos, targets_dict):
        x, y = pos
        symbol = Symbol.from_obs(self.env.obs, x, y)
        if pos not in self.unable_pos:
            if symbol == Symbols.STAIR_UP_CHAR:
                targets_dict[TARGET_TYPES.STAIRS_DOWN.name].append(pos)
            elif symbol == Symbols.KEY_CHAR:
                targets_dict[TARGET_TYPES.KEY.name].append(pos)
            elif symbol in Symbols.CORRIDOR_CHARS and pos not in self.visited_corridors:
                targets_dict[TARGET_TYPES.UNEXPLORED_CORRIDOR.name].append(pos)
            elif symbol in [Symbols.FLOOR_CHAR] + Symbols.DOOR_OPEN_CHARS and self._valid_discover_floor(pos):
                targets_dict[TARGET_TYPES.UNEXPLORED_FLOOR.name].append(pos)
            elif symbol in Symbols.DOOR_CLOSE_CHARS and self._valid_discover_floor(pos):
                targets_dict[TARGET_TYPES.UNEXPLORED_FLOOR_CLOSE.name].append(pos)

    def _find_targets(self):
        frontier = [self.start]
        visited = []
        targets_dict = {key.name: [] for key in TARGET_TYPES}
        while len(frontier) > 0:
            curr = frontier.pop(0)
            self._check_terget(curr, targets_dict)
            for kx, ky in NEIGHBORS_STEPS.keys():
                neighbor = curr[0] + kx, curr[1] + ky
                if self._is_valid_move(neighbor) and neighbor not in visited + frontier:
                    frontier.append(neighbor)
            visited.append(curr)
        for target_type in [TARGET_TYPES.STAIRS_DOWN, TARGET_TYPES.KEY, TARGET_TYPES.UNEXPLORED_FLOOR,
                            TARGET_TYPES.UNEXPLORED_CORRIDOR, TARGET_TYPES.UNEXPLORED_FLOOR_CLOSE]:
            value = targets_dict[target_type.name]
            if len(value) > 0:
                self.targets_poss = value
                break
        print(targets_dict)

    def _is_valid_move(self, neighbor):
        neighbor_symbol = Symbol.from_obs(self.env.obs, neighbor[0], neighbor[1])
        return neighbor_symbol in Symbols.WALKABLE_SYMBOLS + Symbols.DOOR_CLOSE_CHARS and neighbor not in self.unable_pos

    def _astar(self):
        self.g[self.start] = 0
        self.h[self.start] = self.heuristic(self.env, self.start, self.targets_poss)
        curr = self.start
        while len(self.open_list) > 0:
            self.open_list.sort(key=self._f)
            curr = self.open_list.pop(0)
            if curr in self.targets_poss:
                break
            for kx, ky in NEIGHBORS_STEPS.keys():
                neighbor = curr[0] + kx, curr[1] + ky
                if self._is_valid_move(neighbor):
                    neighbor_curr_g = self.g[curr] + 1
                    if neighbor in self.open_list:
                        if self.g[neighbor] <= neighbor_curr_g:
                            continue
                    elif neighbor in self.close_list:
                        if self.g[neighbor] <= neighbor_curr_g:
                            continue
                        del self.close_list[neighbor]
                    else:
                        self.h[neighbor] = self.heuristic(self.env, neighbor, self.targets_poss)
                    self.open_list.append(neighbor)
                    self.g[neighbor] = neighbor_curr_g
            self.close_list.append(curr)
        self.trg = curr

    def _extract_actions(self):
        actions = []
        visited = []
        curr = self.trg
        while curr != self.start:
            neighbors: list[tuple[int, int]] = []
            px, py = curr
            visited.append(curr)
            for kx, ky in NEIGHBORS_STEPS.keys():
                key = (px + kx, py + ky)
                if key in self.close_list:
                    neighbors.append(key)
            neighbors.sort(key=self._f)
            for neighbor in neighbors:
                if neighbor not in visited:
                    diff_x = curr[0] - neighbor[0]
                    diff_y = curr[1] - neighbor[1]
                    action = NEIGHBORS_STEPS[(diff_x, diff_y)]
                    actions.append(action)
                    curr = neighbor
                    break
        actions.reverse()
        return actions
