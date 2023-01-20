from time import sleep
from typing import Callable

import gym
import minihack
from nle import nethack
from tqdm import tqdm
from nle.nethack import CompassDirection as directions

from src.minihack.actions import ACTIONS, ACTIONS_DICT
from src.minihack.symbol import Symbol, Symbols
from src.minihack.desfile import gen_desfile


class Env:

    NEIGHBORS_STEPS = {
        (-1, 0): directions.N,
        (1, 0): directions.S,
        (0, -1): directions.W,
        (0, 1): directions.E
    }

    NEIGHBORS_STEPS_INV = {action: diff for diff, action in NEIGHBORS_STEPS.items()}

    def __init__(self, all_visible: bool = False, actions: list[nethack.Command] = ACTIONS,
                 max_episode_steps: int = 1000):
        self.max_episode_steps = max_episode_steps
        self.env = gym.make(
            "MiniHack-Navigation-Custom-v0",
            des_file=gen_desfile(all_visible),
            actions=actions,
            max_episode_steps=max_episode_steps,
        )
        self.pbar = None
        self.obs = self.env.reset()
        self.reward = 0
        self.done = False
        self.info = None
        self.shape = nethack.OBSERVATION_DESC.get('chars')['shape']
        self.over_hero_symbol = None
        self.step_callback = None

    def find_all_chars_pos(self, symbols: list[Symbol] = [Symbols.HERO_CHAR]):
        poss = []
        for x in range(self.shape[0]):
            for y in range(self.shape[1]):
                if Symbol.from_obs(self.obs, x, y) in symbols:
                    poss.append((x, y))
        return poss

    def find_first_char_pos(self, char: Symbol = Symbols.HERO_CHAR):
        res = self.find_all_chars_pos([char])
        return res[0] if len(res) > 0 else None

    def close_to(self, symbol_list1: list[Symbol], symbol_list2: list[Symbol]):
        for symbol1 in symbol_list1:
            for symbol2 in symbol_list2:
                symbols1 = self.find_all_chars_pos([symbol1])
                symbols2 = self.find_all_chars_pos([symbol2])
                src, trg = (symbols1, symbol2) if len(symbols1) < len(symbols2) else (symbols2, symbol1)
                for x1, y1 in src:
                    for xn in range(-1, 2, 1):
                        for yn in range(-1, 2, 1):
                            if x1 == 0 and y1 == 0:
                                continue
                            loc = x1 + xn, y1 + yn
                            if trg == Symbol(self.obs['chars'][loc], self.obs['colors'][loc]):
                                return True
        return False

    def reset(self):
        self.obs = self.env.reset()
        self.done = False
        self.pbar = tqdm(total=self.env._max_episode_steps)
        return self.obs

    def step(self, step):
        old_hero = self.find_first_char_pos()
        if step in Env.NEIGHBORS_STEPS_INV:
            trg_pos = Env.NEIGHBORS_STEPS_INV[step]
            trg_symbol = Symbol.from_obs(self.obs, old_hero[0] + trg_pos[0], old_hero[1] + trg_pos[1])
        self.obs, self.reward, self.done, self.info = self.env.step(ACTIONS_DICT[step])
        self.pbar.update(1)
        if self.done:
            self.pbar.close()
        if step in Env.NEIGHBORS_STEPS_INV and old_hero != self.find_first_char_pos():
            self.over_hero_symbol = trg_symbol
        if self.step_callback is not None:
            self.step_callback()
        return self.obs, self.reward, self.done, self.info

    def render(self, sleep_time: float = 0.2):
        self.env.render()
        sleep(sleep_time)

    def __len__(self):
        return self.shape

    def iter(self, callback: Callable):
        max_x, max_y = self.shape
        for px in range(max_x):
            for py in range(max_y):
                symbol = Symbol(self.obs["chars"][px, py], self.obs["colors"][px, py])
                callback(symbol, (px, py))

    def iter_neighbors(self, px: int, py: int, callback: Callable):
        max_x, max_y = self.shape
        for kx in range(-1, 2, 1):
            for ky in range(-1, 2, 1):
                if kx == 0 and ky == 0 or not (0 <= px + kx < max_x) or not (0 <= py + ky < max_y):
                    continue
                pos = px + kx, py + ky
                symbol = Symbol(self.obs["chars"][pos], self.obs["colors"][pos])
                callback(symbol, (px, py), (kx, ky))

    def get_neighbors(self, pos=None) -> list[tuple[Symbol, tuple[float, float]]]:
        if pos is None:
            x, y = self.find_first_char_pos(Symbols.HERO_CHAR)
        else:
            x, y = pos
        neighbors = []
        for kx in range(-1, 2, 1):
            for ky in range(-1, 2, 1):
                if kx != 0 and ky != 0:
                    px = x + kx
                    py = y + ky
                    symbol = Symbol(self.obs["chars"][px, py], self.obs["colors"][px, py])
                    neighbors.append((symbol, (px, py)))
        return neighbors