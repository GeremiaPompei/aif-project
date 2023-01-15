import torch

from src.domain import AlgorithmRunner
from src.minihack.env import Env
from src.rl.dqn import DQN
from src.rl.replay_memory import ReplayMemory
from torch import optim, nn

BATCH_SIZE = 128
GAMMA = 0.99
TAU = 0.005


class RLRunner(AlgorithmRunner):
    def __init__(self, env: Env):
        self.env = None
        if env is not None:
            self.init_env(env)

    def init_env(self, env: Env) -> None:
        self.env = env

    def run(self, verbose: bool = True) -> tuple[bool, float, float, float, float]:
        self.env.reset()
        if verbose:
            self.env.render()
        target_net = DQN()
        policy_net = DQN()
        reply_memory = ReplayMemory(100)
        next_state = None
        while not self.env.done:
            state = self.env.obs["chars"]
            action = policy_net.select_action(state)
            self.env.step(action.item())
            reply_memory.push(state=state, action=action, next_state=next_state, reward=self.env.reward)
            next_state = state
            self.optimize_model(reply_memory, policy_net, target_net)
            target_net_state_dict = target_net.state_dict()
            policy_net_state_dict = policy_net.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
            target_net.load_state_dict(target_net_state_dict)
            self.env.step(1)
            if verbose:
                self.env.render()

    def optimize_model(self, reply_memory: ReplayMemory, policy_net: DQN, target_net: DQN):
        optimizer = optim.AdamW(policy_net.parameters())
        if len(reply_memory.memory) < BATCH_SIZE:
            return
        batch = reply_memory.sample(BATCH_SIZE)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch["next_state"])))
        non_final_next_states = torch.cat([s for s in batch["next_state"]
                                           if s is not None])
        state_batch = torch.cat(batch["state"])
        action_batch = torch.cat(batch["action"])
        reward_batch = torch.cat(batch["reward"])

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
