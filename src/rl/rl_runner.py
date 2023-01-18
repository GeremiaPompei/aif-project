import numpy as np
import torch

from src.domain import AlgorithmRunner
from src.minihack.actions import ACTIONS
from src.minihack.env import Env
from src.rl.dqn import DQN
from src.rl.replay_memory import ReplayMemory
from torch import optim, nn

BATCH_SIZE = 32
GAMMA = 0.99
TAU = 0.005


class RLRunner(AlgorithmRunner):
    def __init__(self, env: Env):
        self.env = None
        if env is not None:
            self.init_env(env)

    def init_env(self, env: Env) -> None:
        self.env = env

    def run(self, n_env: int = 1000, verbose: bool = True) -> tuple[bool, float, float, float, float]:
        for i in range(n_env):
            print(f"Env n.{i}")
            self.env.reset()
            if verbose:
                if i < n_env / 3:
                    self.env.render()
            target_net = DQN()
            policy_net = DQN()
            reply_memory = ReplayMemory(100)
            next_state = None
            while not self.env.done:
                state = torch.Tensor([[self.env.obs["chars"], self.env.obs["colors"]]])
                action = policy_net.select_action(state)
                self.env.step(ACTIONS[action])
                reply_memory.push(state=state, action=action, next_state=next_state, reward=self.env.reward)
                next_state = state
                self.optimize_model(reply_memory, policy_net, target_net)
                target_net_state_dict = target_net.state_dict()
                policy_net_state_dict = policy_net.state_dict()
                for key in policy_net_state_dict:
                    target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
                target_net.load_state_dict(target_net_state_dict)
                if verbose:
                    if i > n_env / 3:
                        self.env.render(sleep_time=0.2)

    def optimize_model(self, reply_memory: ReplayMemory, policy_net: DQN, target_net: DQN):
        if len(reply_memory.memory) < BATCH_SIZE:
            return
        optimizer = optim.AdamW(policy_net.parameters())
        batch = reply_memory.sample(BATCH_SIZE)
        non_final_mask = torch.tensor(tuple(map(lambda s: s["next_state"] is not None,
                                                batch)))
        non_final_next_states = torch.cat([torch.tensor(s["next_state"]) for s in batch
                                           if s["next_state"] is not None])
        state_batch = torch.cat([torch.tensor(s["state"]) for s in batch])
        action_batch = torch.cat([s["action"].view(1, 1) for s in batch])
        reward_batch = torch.cat([torch.tensor([s["reward"]]) for s in batch])

        state_action_values = policy_net(state_batch).gather(1, action_batch)

        next_state_values = torch.zeros(BATCH_SIZE)
        with torch.no_grad():
            next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0]
        expected_state_action_values = (next_state_values * GAMMA) + reward_batch

        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
        optimizer.step()
