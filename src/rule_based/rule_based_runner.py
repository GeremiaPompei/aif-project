from src.domain import AlgorithmRunner
from src.minihack.env import Env
from src.rule_based.rule_based import solution


class RuleBasedRunner(AlgorithmRunner):

    def __init__(self, env: Env = None, verbose: bool = False):
        super(RuleBasedRunner, self).__init__()
        self.verbose = verbose
        if env is not None:
            self.init_env(env)

    def run(self):
        env = self.env.env
        obs = self.env.obs
        if not self.verbose:
            env.render = lambda: None
        old_step_callback = env.step

        def step_callback(x):
            res = old_step_callback(x)
            self.one_more_step()
            return res

        env.step = step_callback

        self.win, self.total_steps, self.steps_first_key, self.steps_first_door, self.steps_first_corridor = \
            solution(env, obs, _verbose=self.verbose)
