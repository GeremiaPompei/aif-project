from typing import Callable

import gym
import minihack
from nle import nethack
from functools import reduce
import numpy as np

from src.data_structure.graph import EOS
from src.minihack.actions import ACTIONS
from src.minihack.mh_graph import MHGraph


class Env:
    def __init__(self, actions: list[nethack.Command] = ACTIONS, max_episode_steps: int = 1000):
        self.env = gym.make(
            "MiniHack-Navigation-Custom-v0",
            des_file="src/minihack/desfile.des",
            actions=actions,
            max_episode_steps=max_episode_steps,
        )
        self.obs = self.env.reset()
        self.reward = 0
        self.done = False
        self.info = None
        self.shape = self.obs['chars'].shape

        self.graph = MHGraph(self)

    def find_all_chars_pos(self, chars: list[str] = ['@']):
        return reduce(lambda x, y: x + y, [np.argwhere(self.obs['chars'] == ord(char)).tolist() for char in chars])

    def find_first_char_pos(self, char: str = '@'):
        res = self.find_all_chars_pos([char])
        return res if len(res) > 0 else None

    def close_to(self, char_list1: str, char_list2: str):
        for char1 in char_list1:
            for char2 in char_list2:
                chars1 = self.find_all_chars_pos([char1])
                chars2 = self.find_all_chars_pos([char2])
                src, trg = (chars1, char2) if len(chars1) < len(chars2) else (chars2, char1)
                for x1, y1 in src:
                    for xn in range(-1, 2, 1):
                        for yn in range(-1, 2, 1):
                            if x1 == 0 and y1 == 0:
                                continue
                            if ord(trg) == self.obs['chars'][x1 + xn, y1 + yn]:
                                return True
        return False

    def reset(self):
        self.obs = self.env.reset()
        return self.obs

    def step(self, step):
        self.obs, self.reward, self.done, self.info = self.env.step(step)
        return self.obs, self.reward, self.done, self.info

    def render(self):
        self.env.render()

    def __len__(self):
        return self.shape

    def iter(self, callback: Callable):
        max_x, max_y = self.shape
        for px in range(max_x):
            for py in range(max_y):
                callback(self.obs["chars"][px, py], (px, py))

    def iter_neighbors(self, px: int, py: int, callback: Callable):
        max_x, max_y = self.shape
        for kx in range(-1, 2, 1):
            for ky in range(-1, 2, 1):
                if kx == 0 and ky == 0 or not (0 <= px + kx < max_x) or not (0 <= py + ky < max_y):
                    continue
                callback(self.obs["chars"][px + kx, py + ky], (px, py), (kx, ky))
