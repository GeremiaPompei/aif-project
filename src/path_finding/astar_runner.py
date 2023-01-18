from typing import Callable

from src.data_structure.graph import Node
from src.domain import AlgorithmRunner
from src.minihack.env import Env
from src.minihack.symbol import Symbols, Symbol
from src.path_finding.astar import AStar


class AStarRunner(AlgorithmRunner):

    def __init__(self, heuristic: Callable = None, env: Env = None):
        self.targets_list = [[Symbols.STAIR_UP_CHAR], [Symbols.KEY_CHAR],
                             Symbols.DOOR_OPEN_CHARS, Symbols.CORRIDOR_CHARS,
                             Symbols.DOOR_CLOSE_CHARS, [Symbols.OBSCURE_CHAR]]
        self.walkable_symbols = Symbols.DOOR_CLOSE_CHARS + Symbols.WALKABLE_SYMBOLS
        self.env = None
        self.algorithm = None
        self.profiler = None
        self.heuristic = heuristic
        if env is not None:
            self.init_env(env)

    def init_env(self, env: Env):
        self.env = env
        self.algorithm = AStar(env, self.heuristic)

    def run(self, verbose: bool = True) -> tuple[bool, int, float, float, float]:
        self.env.reset()
        if verbose:
            self.env.render()
        total_steps, steps_first_key, steps_first_door, steps_first_corridor = 0, None, None, None
        while not self.env.done:
            if self.env.over_hero_symbol == Symbols.STAIR_UP_CHAR:
                break
            total_steps += self.algorithm.find()
            print(f"Step {total_steps}/{self.env.max_episode_steps}", flush=True)
            if steps_first_key is None and self.env.over_hero_symbol == Symbols.KEY_CHAR:
                steps_first_key = total_steps
            if steps_first_door is None and \
                    self.env.over_hero_symbol in Symbols.DOOR_OPEN_CHARS + Symbols.DOOR_CLOSE_CHARS:
                steps_first_door = total_steps
            if steps_first_corridor is None and self.env.over_hero_symbol in Symbols.CORRIDOR_CHARS:
                steps_first_corridor = total_steps
        return (self.env.over_hero_symbol == Symbols.STAIR_UP_CHAR), total_steps, steps_first_key, steps_first_door, steps_first_corridor

    def __str__(self):
        return f"AStar({self.heuristic.__name__ if self.heuristic is not None else ''})"
