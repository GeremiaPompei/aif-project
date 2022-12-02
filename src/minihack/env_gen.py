import gym
import minihack

from src.minihack.actions import ACTIONS


def gen_minihack_env():
    return gym.make(
        "MiniHack-Navigation-Custom-v0",
        des_file="src/minihack/desfile.des",
        actions=ACTIONS,
        max_episode_steps=50,
    )
