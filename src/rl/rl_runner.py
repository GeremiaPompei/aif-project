from pathlib import Path

import numpy as np
import torch
from src.domain import AlgorithmRunner
from src.minihack.actions import ACTIONS
from src.minihack.env import Env
from src.minihack.symbol import Symbols
from src.rl.dqn import DQN
from src.rl.replay_memory import ReplayMemory, Record
from torch import optim, nn
import math
import random
import logging as lg


def _compute_reward(env, history_reward: dict):
    visible_chars = len(env.find_all_chars_pos([Symbols.OBSCURE_CHAR]))
    if "last_visible_chars" in history_reward:
        visible_chars -= history_reward["last_visible_chars"]
    history_reward["last_visible_chars"] = visible_chars
    reward = env.reward + visible_chars / (env.shape[0] * env.shape[1])
    trg_pos = env.find_first_char_pos(Symbols.STAIR_UP_CHAR)
    if trg_pos is not None:
        curr = env.find_first_char_pos(Symbols.HERO_CHAR)
        reward = 50 / ((trg_pos[0] - curr[0]) ** 2 + (trg_pos[1] - curr[1]) ** 2)
    return reward


class RLRunner(AlgorithmRunner):
    def __init__(self, env: Env = None,
                 model_filename: str = "DQN.torch",
                 eps_start: float = 0.9,
                 eps_end: float = 0.05,
                 eps_decay: int = 1000,
                 sleep_time: float = -1):
        super(RLRunner, self).__init__()
        self.model_filename = model_filename
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.sleep_time = sleep_time
        self.policy_net = DQN()
        if model_filename is not None and Path(model_filename).exists():
            self.policy_net.load_state_dict(torch.load(self.model_filename))
        if env is not None:
            self.init_env(env)

    def _state_from_obs(self, env: Env = None):
        if env is None:
            env = self.env
        return torch.Tensor(np.array([[env.obs["chars"], env.obs["colors"]]]))

    def run(self, env: Env = None,
            memory_size: int = 3000,
            batch_size: int = 32,
            gamma: float = 0.99,
            verbose: bool = False,
            save_model: bool = False):
        if env is None:
            env = self.env
        reply_memory = ReplayMemory(memory_size)
        next_state = None
        steps, total_reward, total_loss, loss_count = 0, 0, 0, 0
        history_reward = {}
        while not env.done:
            state = self._state_from_obs(env)
            action = self._select_action(state, steps)
            env.step(ACTIONS[action])
            steps += 1
            if self.env is not None:
                self.one_more_step()
            reward = env.reward + _compute_reward(env, history_reward)
            total_reward += reward
            reply_memory.push(Record(state=state, action=action, next_state=next_state, reward=reward))
            next_state = state
            if len(reply_memory.memory) >= batch_size:
                loss = self._optimize_model(reply_memory.sample(batch_size), batch_size, gamma)
                total_loss += loss
                loss_count += 1
            if self.sleep_time > 0:
                env.render(sleep_time=self.sleep_time)
        if verbose:
            lg.info(f"Steps: {steps}")
            lg.info(f"Total reward: {total_reward}")
            lg.info(f"Mean loss: {round(total_loss / loss_count, 4)}")
            lg.info(f"Status: {'Win' if env.over_hero_symbol == Symbols.STAIR_UP_CHAR else 'Lost'}")
        if self.model_filename is not None and save_model:
            torch.save(self.policy_net.state_dict(), self.model_filename)

    def train(self, env: Env,
              n_env: int = 1000,
              memory_size: int = 100,
              batch_size: int = 64,
              gamma: float = 0.99,
              verbose: bool = True):
        for i in range(n_env):
            lg.info(f"Env n.{i + 1}")
            env.reset()
            self.run(env=env, memory_size=memory_size, batch_size=batch_size, gamma=gamma, verbose=verbose,
                     save_model=True)

    def _select_action(self, state: torch.Tensor, steps: int):
        sample = random.random()
        eps_threshold = self.eps_end + (self.eps_start - self.eps_end) * math.exp(-1. * steps / self.eps_decay)
        if sample > eps_threshold:
            with torch.no_grad():
                return self.policy_net(state).argmax(1)[0]
        else:
            return torch.tensor(random.sample(range(len(ACTIONS)), 1)[0])

    def _optimize_model(self, batch: list[Record], batch_size: int, gamma: float):
        criterion = nn.SmoothL1Loss()
        optimizer = optim.AdamW(self.policy_net.parameters())

        # batches
        state_batch = torch.cat([torch.tensor(s.state) for s in batch])
        action_batch = torch.cat([s.action.view(1, 1) for s in batch])
        reward_batch = torch.cat([torch.tensor([s.reward]) for s in batch])

        # expected action values
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)
        next_state_values = torch.zeros(batch_size)
        non_final_mask = torch.tensor([s.next_state is not None for s in batch])
        non_final_next_states = torch.cat([torch.tensor(s.next_state) for s in batch if s.next_state is not None])
        with torch.no_grad():
            next_state_values[non_final_mask] = self.policy_net(non_final_next_states).max(1)[0]
        target = (next_state_values * gamma) + reward_batch

        # update weights
        loss = criterion(state_action_values, target.unsqueeze(1))
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        optimizer.step()
        return loss.item()

    def __str__(self):
        return "ReinforcementLearning(DQN)"
