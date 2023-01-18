from src.minihack import Env
from src.rl import RLRunner

rl_runner = RLRunner()
env = Env(max_episode_steps=10000)
rl_runner.train(env, n_env=1000)
