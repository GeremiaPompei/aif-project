import typing as tp
import time

from memory_profiler import profile
from src.minihack.env import Env

import logging as lg
import sys

root = lg.getLogger()
root.setLevel(lg.INFO)

handler = lg.StreamHandler(sys.stdout)
handler.setLevel(lg.DEBUG)
formatter = lg.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


def memory_measure(callable: tp.Callable):
    @profile
    def callback():
        callable()


class AlgorithmProfiler:

    def __init__(self, algorithm: tp.Callable, n: int = 0):
        """
        Initialize the profiler
        :param algorithm: the algorithm to be called
        :param n: the number of environment to generate
        """
        self._total_steps = 0
        self._steps_first_door = 0
        self._steps_first_key = 0
        self._steps_first_corridor = 0
        self._total_wins = 0
        self._n = n
        self._envs_: tp.List[Env] = []
        self._algo = algorithm
        self._execution_time = 0

    def _generate_env(self) -> Env:
        """
        Generate a new environment.
        :return: Env object
        """
        env = Env(all_visible=False)
        self._envs_.append(env)
        return env

    def profile(self):
        for i in range(self._n):
            lg.info(f"Round {i + 1}/{self._n}")

            env = self._generate_env()
            algorithm = self._algo(env, self)
            # profile memory

            # collect time
            start = time.time()

            # run algorithm
            win, total_steps, steps_first_key, steps_first_door, steps_first_corridor = algorithm.run(verbose=False)

            end = time.time()
            self._execution_time += end - start

            lg.info("Win" if win else "Lost")
            if win:
                self._total_wins += 1

            lg.info(f"Total steps: {total_steps}")
            self._total_steps += total_steps

            if steps_first_key is not None:
                lg.info(f"Steps first key: {steps_first_key}")
                self._steps_first_key += steps_first_key

            if steps_first_door is not None:
                lg.info(f"Steps first door: {steps_first_door}")
                self._steps_first_door += steps_first_door

            if steps_first_corridor is not None:
                lg.info(f"Steps first corridor: {steps_first_corridor}")
                self._steps_first_corridor += steps_first_corridor


    def compute_metrics(self) -> tp.Dict[str, float]:
        total_steps = float(self._total_steps / self._n)
        steps_first_door = float(self._steps_first_door / self._n)
        steps_first_key = float(self._steps_first_key / self._n)
        steps_first_corridor = float(self._steps_first_corridor / self._n)
        total_lost = self._n - self._total_wins

        return {
            "total_steps": total_steps,
            "steps_first_door": steps_first_door,
            "steps_first_key": steps_first_key,
            "steps_first_corridor": steps_first_corridor,
            "total_run": self._n,
            "total_wins": self._total_wins,
            "total_lost": total_lost

        }

