from enum import Enum
from src.domain import AlgorithmRunner
from src.minihack.env import Env
from src.minihack.symbol import Symbols, Symbol
from nle.nethack import Command as cmd
from src.path_finding.path_finding_algorithm import PathFindingAlgorithm


class TARGET_TYPES(Enum):
    KEY = 1
    UNEXPLORED_CORRIDOR = 2
    UNEXPLORED_FLOOR = 3
    STAIRS_DOWN = 4
    UNEXPLORED_FLOOR_CLOSE = 5


class PathFindingRunner(AlgorithmRunner):

    def __init__(self, algorithm: PathFindingAlgorithm = None, env: Env = None, sleep_time: float = -1):
        super(PathFindingRunner, self).__init__()
        self.algorithm = algorithm
        self.sleep_time = sleep_time
        self.visited_corridors = set()
        self.unable_pos = set()
        if env is not None:
            self.init_env(env)

    def init_env(self, env: Env):
        super(PathFindingRunner, self).init_env(env)
        self.algorithm.env = self.env

    def run(self) -> tuple[bool, int, float, float, float]:
        self.env.reset()
        self.visited_corridors = set()
        self.unable_pos = set()
        if self.sleep_time > 0:
            self.env.render(self.sleep_time)
        while not self.env.done:
            if self.env.over_hero_symbol == Symbols.STAIR_UP_CHAR:
                break
            target_poss = self._find_targets()
            actions = self.algorithm.find_actions(target_poss, self._is_valid_move)

            for action in actions:
                curr = self.env.find_first_char_pos()
                next_step_diff = PathFindingAlgorithm.NEIGHBORS_STEPS_INV[action]
                next_step = (curr[0] + next_step_diff[0], curr[1] + next_step_diff[1])
                next_step_symbol = Symbol.from_obs(self.env.obs, next_step[0], next_step[1])
                if next_step_symbol in Symbols.DOOR_CLOSE_CHARS:
                    self.env.step(cmd.APPLY)
                    if self.sleep_time > 0:
                        self.env.render(self.sleep_time)
                if not self.env.done:
                    self.env.step(action, next_step_symbol)
                    if self.sleep_time > 0:
                        self.env.render(self.sleep_time)
                    if not self.env.done:
                        next_step_symbol_updated = Symbol.from_obs(self.env.obs, next_step[0], next_step[1])
                        if next_step_symbol_updated in Symbols.DOOR_CLOSE_CHARS \
                                or (next_step_symbol_updated not in Symbols.DOOR_OPEN_CHARS
                                    and self.env.find_first_char_pos() != next_step):
                            self.unable_pos.add(next_step)
                        if self.env.over_hero_symbol in Symbols.CORRIDOR_CHARS:
                            self.visited_corridors.add(self.env.find_first_char_pos(Symbols.HERO_CHAR))

                if self.env.done:
                    break

    def _valid_discover_floor(self, pos):
        for kx, ky in PathFindingAlgorithm.NEIGHBORS_STEPS.keys():
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
        frontier = [self.env.find_first_char_pos()]
        visited = []
        targets_dict = {key.name: [] for key in TARGET_TYPES}
        while len(frontier) > 0:
            curr = frontier.pop(0)
            self._check_terget(curr, targets_dict)
            for kx, ky in PathFindingAlgorithm.NEIGHBORS_STEPS.keys():
                neighbor = curr[0] + kx, curr[1] + ky
                if self._is_valid_move(neighbor) and neighbor not in visited + frontier:
                    frontier.append(neighbor)
            visited.append(curr)
        for target_type in [TARGET_TYPES.STAIRS_DOWN, TARGET_TYPES.KEY, TARGET_TYPES.UNEXPLORED_FLOOR,
                            TARGET_TYPES.UNEXPLORED_CORRIDOR, TARGET_TYPES.UNEXPLORED_FLOOR_CLOSE]:
            value = targets_dict[target_type.name]
            if len(value) > 0:
                return value
        return []

    def _is_valid_move(self, neighbor):
        neighbor_symbol = Symbol.from_obs(self.env.obs, neighbor[0], neighbor[1])
        return neighbor_symbol in Symbols.WALKABLE_SYMBOLS + Symbols.DOOR_CLOSE_CHARS and neighbor not in self.unable_pos

    def __str__(self):
        return f"PathFinding({str(self.algorithm)})"
