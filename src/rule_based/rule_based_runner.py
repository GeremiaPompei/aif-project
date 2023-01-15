from src.domain import AlgorithmRunner
from src.minihack.env import Env
from src.rule_based.rule_based import solution


class RuleBasedRunner(AlgorithmRunner):

    def __init__(self, env: Env = None):
        self.env = None
        if env is not None:
            self.init_env(env)

    def init_env(self, env: Env):
        self.env = env

    def run(self, verbose: bool = True) -> tuple[bool, int, float, float, float]:
        is_win, overall_steps, first_key_step, first_door_step, first_corridor_step = solution(self.env.env, self.env.obs)