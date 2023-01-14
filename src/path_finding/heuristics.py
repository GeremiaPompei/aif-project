from src.minihack.env import Env
import math

from src.minihack.symbol import Symbol, Symbols


class Heuristics:

    @staticmethod
    def manhattan(env: Env, hero_pos: tuple[int, int], target_poss: list[tuple[int, int]]):
        x_hero, y_hero = hero_pos
        dist = 0
        for x_target, y_target in target_poss:
            dist += abs(x_hero - x_target) + abs(y_hero - y_target)
        return dist / len(target_poss)

    @staticmethod
    def euclidean(env: Env, hero_pos: tuple[int, int], target_poss: list[tuple[int, int]]):
        x_hero, y_hero = hero_pos
        dist = 0
        for x_target, y_target in target_poss:
            dist += math.sqrt((x_hero - x_target) ** 2 + (y_hero - y_target) ** 2)
        return dist / len(target_poss)

    @staticmethod
    def walkable_steps_in_matrix(env: Env, hero_pos: tuple[int, int], target_poss: list[tuple[int, int]]):
        x_hero, y_hero = hero_pos
        dist = 0
        for x_target, y_target in target_poss:
            single_dist = 0
            for x in range(min(x_hero, x_target), max(x_hero, x_target) + 1):
                for y in range(min(y_hero, y_target), max(y_hero, y_target) + 1):
                    if Symbol(env.obs["chars"][x, y], env.obs["colors"][x, y]) in Symbols.WALKABLE_SYMBOLS:
                        single_dist += 1
            dist += single_dist
        return dist / len(target_poss)
