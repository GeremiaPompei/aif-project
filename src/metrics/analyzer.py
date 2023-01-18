import os
import time

import psutil

from src.domain import AlgorithmRunner
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


class Analyzer:

    def __init__(self, algorithms: list[AlgorithmRunner], env_n: int, max_episode_steps: int = None):
        """
        Initialize the profiler
        :param algorithms (AlgorithmRunner): the algorithms to be called
        :param env_n: number of environments to generate
        """
        self._env_n_ = env_n
        self._algs = algorithms
        self.metrics = {}
        self._max_episode_steps = max_episode_steps

    def _generate_env(self) -> Env:
        """
        Generate a new environment.
        :return: Env object
        """
        return Env(all_visible=False, max_episode_steps=self._max_episode_steps)

    def analyze(self):
        n = self._env_n_
        for algo in self._algs:
            total_steps = 0
            steps_first_door = 0
            steps_first_key = 0
            steps_first_corridor = 0
            total_wins = 0
            execution_time = 0
            memory_usage = 0
            for i in range(n):
                lg.info(f"Round {i + 1}/{n}")

                env = self._generate_env()
                algo.init_env(env)

                process = psutil.Process(os.getpid())

                # collect time
                start = time.time()

                # run algorithm
                win, ts, sfk, sfd, sfc = algo.run()

                mu = process.memory_info().rss

                end = time.time()
                et = end - start
                lg.info(f"Execution time: {et}")
                execution_time += et

                lg.info(f"Memory usage: {mu} bytes")
                memory_usage += mu

                lg.info("Win" if win else "Lost")
                if win:
                    total_wins += 1

                lg.info(f"Total steps: {ts}")
                total_steps += ts

                if sfk is not None:
                    lg.info(f"Steps first key: {sfk}")
                    steps_first_key += sfk

                if sfd is not None:
                    lg.info(f"Steps first door: {sfd}")
                    steps_first_door += sfd

                if sfc is not None:
                    lg.info(f"Steps first corridor: {sfc}")
                    steps_first_corridor += sfc

            total_steps = float(total_steps / n)
            steps_first_door = float(steps_first_door / n)
            steps_first_key = float(steps_first_key / n)
            steps_first_corridor = float(steps_first_corridor / n)
            execution_time = float(execution_time / n)
            memory_usage = float(memory_usage / n)
            total_lost = n - total_wins

            self.metrics[str(algo)] = {
                "total_steps": total_steps,
                "steps_first_door": steps_first_door,
                "steps_first_key": steps_first_key,
                "steps_first_corridor": steps_first_corridor,
                "total_run": n,
                "total_wins": total_wins,
                "total_lost": total_lost,
                "execution_time": execution_time,
                "memory_usage": memory_usage,
            }

