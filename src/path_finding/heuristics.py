from src.minihack.env import Env
import math

from src.minihack.symbol import Symbol, Symbols


def _compute_mean(target_poss: list[tuple[int, int]], callback):
    if len(target_poss) == 0:
        return 0
    dist = 0
    for x_target, y_target in target_poss:
        dist += callback(x_target, y_target)
    return dist / len(target_poss)


class Heuristics:

    @staticmethod
    def manhattan(env: Env, hero_pos: tuple[int, int], target_poss: list[tuple[int, int]]):
        return _compute_mean(
            target_poss,
            lambda x_target, y_target: abs(hero_pos[0] - x_target) + abs(hero_pos[1] - y_target),
        )

    @staticmethod
    def euclidean(env: Env, hero_pos: tuple[int, int], target_poss: list[tuple[int, int]]):
        return _compute_mean(
            target_poss,
            lambda x_target, y_target: math.sqrt((hero_pos[0] - x_target) ** 2 + (hero_pos[1] - y_target) ** 2),
        )

    @staticmethod
    def not_walkable_steps_in_matrix(env: Env, hero_pos: tuple[int, int], target_poss: list[tuple[int, int]]):
        def callback(x_target, y_target):
            dist = 0
            for x in range(min(hero_pos[0], x_target), max(hero_pos[0], x_target) + 1):
                for y in range(min(hero_pos[1], y_target), max(hero_pos[1], y_target) + 1):
                    if not Symbol.from_obs(env.obs, x, y) in Symbols.WALKABLE_SYMBOLS:
                        dist += 1
            return dist
        return _compute_mean(target_poss, callback)
