from src.minihack.env import Env
import math

from src.minihack.symbol import Symbol, Symbols


class Heuristics:

    @staticmethod
    def manhattan(env: Env, hero_pos: tuple[int, int], target_pos: tuple[int, int]):
        x_hero, y_hero = hero_pos
        x_target, y_target = target_pos
        return abs(x_hero - x_target) + abs(y_hero - y_target)

    @staticmethod
    def euclidean(env: Env, hero_pos: tuple[int, int], target_pos: tuple[int, int]):
        x_hero, y_hero = hero_pos
        x_target, y_target = target_pos
        return math.sqrt((x_hero - x_target) ** 2 + (y_hero - y_target) ** 2)

    @staticmethod
    def walkable_steps_in_matrix(env: Env, hero_pos: tuple[int, int], target_pos: tuple[int, int]):
        x_hero, y_hero = hero_pos
        x_target, y_target = target_pos
        single_dist = 0
        for x in range(min(x_hero, x_target), max(x_hero, x_target) + 1):
            for y in range(min(y_hero, y_target), max(y_hero, y_target) + 1):
                if Symbol(env.obs["chars"][x, y], env.obs["colors"][x, y]) not in Symbols.WALKABLE_SYMBOLS:
                    single_dist += 1
        return single_dist
