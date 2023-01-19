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
    def __init__(self, env: Env = None, model_filename: str = "DQN.torch", sleep_time: float = -1):
        super(RLRunner, self).__init__()
        self.model_filename = model_filename
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

    def run(self) -> tuple[bool, float, float, float, float]:
        while not self.env.done:
            state = self._state_from_obs()
            with torch.no_grad():
                action = self.policy_net(state).argmax(1)[0]
            self.env.step(ACTIONS[action])
            self.one_more_step()
            if self.sleep_time > 0:
                self.env.render(sleep_time=self.sleep_time)

    def train(self, env: Env,
              n_env: int = 1000,
              memory_size: int = 100,
              eps_start: float = 0.9,
              eps_end: float = 0.05,
              eps_decay: int = 1000,
              batch_size: int = 32,
              gamma: float = 0.99,
              tau: float = 0.005):
        for i in range(n_env):
            lg.info(f"Env n.{i + 1}")
            env.reset()
            target_net = DQN()
            reply_memory = ReplayMemory(memory_size)
            next_state = None
            steps = 0
            total_reward = 0
            total_loss = 0
            loss_count = 0
            while not env.done:
                state = self._state_from_obs(env)
                eps_threshold = eps_end + (eps_start - eps_end) * math.exp(-1. * steps / eps_decay)
                action = self._select_action(state, eps_threshold)
                env.step(ACTIONS[action])
                steps += 1
                total_reward += env.reward
                reply_memory.push(Record(state=state, action=action, next_state=next_state, reward=env.reward))
                next_state = state
                if len(reply_memory.memory) >= batch_size:
                    loss = self._optimize_model(reply_memory.sample(batch_size), target_net, batch_size, gamma, tau)
                    total_loss += loss
                    loss_count += 1
                self._update_target_weights(target_net, tau)
                if self.sleep_time > 0:
                    env.render(sleep_time=self.sleep_time)
            lg.info(f"Steps: {steps}")
            lg.info(f"Total reward: {total_reward}")
            lg.info(f"Mean loss: {round(total_loss / loss_count, 4)}")
            lg.info(f"Status: {'Win' if env.over_hero_symbol == Symbols.STAIR_UP_CHAR else 'Lost'}")
            if self.model_filename is not None:
                torch.save(self.policy_net.state_dict(), self.model_filename)

    def _select_action(self, state: torch.Tensor, eps_threshold: float):
        sample = random.random()
        if sample > eps_threshold:
            with torch.no_grad():
                return self.policy_net(state).argmax(1)[0]
        else:
            return torch.tensor(random.sample(range(len(ACTIONS)), 1)[0])

    def _optimize_model(self, batch: list[Record], target_net: DQN, batch_size: int, gamma: float, tau: float):
        criterion = nn.SmoothL1Loss()
        optimizer = optim.AdamW(self.policy_net.parameters())

        # batches
        non_final_mask = torch.tensor([s.next_state is not None for s in batch])
        non_final_next_states = torch.cat([torch.tensor(s.next_state) for s in batch if s.next_state is not None])
        state_batch = torch.cat([torch.tensor(s.state) for s in batch])
        action_batch = torch.cat([s.action.view(1, 1) for s in batch])
        reward_batch = torch.cat([torch.tensor([s.reward]) for s in batch])

        # expected action values
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)
        next_state_values = torch.zeros(batch_size)
        with torch.no_grad():
            next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0]
        expected_state_action_values = (next_state_values * gamma) + reward_batch

        # update weights
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        optimizer.step()
        return loss.item()

    def _update_target_weights(self, target_net: DQN, tau: int):
        # mix target_net weights with policy_net according tau parameter
        target_net_state_dict = target_net.state_dict()
        policy_net_state_dict = self.policy_net.state_dict()
        for key in policy_net_state_dict:
            target_net_state_dict[key] = policy_net_state_dict[key] * tau + target_net_state_dict[key] * (1 - tau)
        target_net.load_state_dict(target_net_state_dict)

    def __str__(self):
        return "ReinforcementLearning(DQN)"
