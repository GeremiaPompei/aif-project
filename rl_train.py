from src.minihack.env import Env
from src.rl.rl_runner import RLRunner

rl_runner = RLRunner()
env = Env(max_episode_steps=1000)
rl_runner.train(env, n_env=10000)
