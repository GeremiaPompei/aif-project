from src.minihack import Env
from src.rl import RLRunner

rl_runner = RLRunner()
rl_runner.init_env(Env(max_episode_steps=10000))
rl_runner.train(n_env=1000)
