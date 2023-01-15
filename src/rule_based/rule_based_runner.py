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

    def run(self) -> tuple[bool, int, float, float, float]:
        return solution(self.env.env, self.env.obs)