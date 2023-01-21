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


class RLRunner(AlgorithmRunner):
    def __init__(self, model_filename: str = "DQN.torch",
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

    def _state_from_obs(self):
        return torch.Tensor(np.array([[self.env.obs["chars"], self.env.obs["colors"]]]))

    def run(self,
            reply_memory: ReplayMemory = ReplayMemory(),
            batch_size: int = 32,
            gamma: float = 0.99,
            verbose: bool = False,
            save_model: bool = False):
        self.env.reset()
        steps, total_reward, total_loss, loss_count = 0, 0, 0, 0
        next_state = None
        while not self.env.done:
            state = self._state_from_obs()
            action = self._select_action(state, steps)
            self.env.step(ACTIONS[action])
            steps += 1
            reward = self.env.reward
            total_reward += reward
            if next_state is not None:
                reply_memory.push(Record(state=state, action=action,
                                         next_state=next_state if not self.env.done else torch.zeros(state.shape),
                                         reward=reward))
            next_state = state
            if len(reply_memory.memory) >= batch_size:
                loss = self._optimize_model(reply_memory.sample(batch_size), gamma)
                total_loss += loss
                loss_count += 1
            if self.sleep_time > 0:
                self.env.render(sleep_time=self.sleep_time)
        if verbose:
            lg.info(f"Steps: {steps}")
            lg.info(f"Total reward: {total_reward}")
            lg.info(f"Mean loss: {round(total_loss / loss_count, 4)}")
            lg.info(f"Status: {'Win' if self.env.over_hero_symbol == Symbols.STAIR_UP_CHAR else 'Lost'}")
        if self.model_filename is not None and save_model:
            torch.save(self.policy_net.state_dict(), self.model_filename)

    def train(self,
              n_env: int = 1000,
              memory_size: int = None,
              batch_size: int = 128,
              gamma: float = 0.99,
              verbose: bool = True):
        reply_memory = ReplayMemory(memory_size)
        for i in range(n_env):
            lg.info(f"Env n.{i + 1}")
            self.run(reply_memory=reply_memory, batch_size=batch_size, gamma=gamma, verbose=verbose,
                     save_model=True)

    def _select_action(self, state: torch.Tensor, steps: int):
        sample = random.random()
        eps_threshold = self.eps_end + (self.eps_start - self.eps_end) * math.exp(-1. * steps / self.eps_decay)
        if sample > eps_threshold:
            with torch.no_grad():
                return self.policy_net(state).argmax(1)[0]
        else:
            return torch.tensor(random.sample(range(len(ACTIONS)), 1)[0])

    def _optimize_model(self, batch: list[Record], gamma: float):
        criterion = nn.SmoothL1Loss()
        optimizer = optim.AdamW(self.policy_net.parameters())

        # batches
        state_batch = torch.cat([torch.tensor(s.state) for s in batch])
        next_state_batch = torch.cat([torch.tensor(s.next_state) for s in batch])
        reward_batch = torch.cat([torch.tensor([s.reward]) for s in batch])

        # expected action values
        prediction = self.policy_net(state_batch)
        with torch.no_grad():
            next_state_values = self.policy_net(next_state_batch).max(1)[0]
        target = reward_batch + gamma * next_state_values

        # update weights
        loss = criterion(prediction, target.unsqueeze(1))
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        optimizer.step()
        return loss.item()

    def __str__(self):
        model_name = "DQN"
        if self.model_filename is not None:
            model_name += f"({self.model_filename})"
        else:
            model_name += f"(from-scratch)"
        return f"ReinforcementLearning({model_name})"
