from src.minihack.env import Env
from src.rl.rl_runner import RLRunner

rl = RLRunner(Env(max_episode_steps=100000))

rl.run(verbose=True)