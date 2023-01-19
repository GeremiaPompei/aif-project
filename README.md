# AIF Project: Minihack

## Prerequisite

To install dependencies:
```
pip3 install -r requirements.txt
pip3 install git+https://github.com/GeremiaPompei/minihack
```

## RL training
Reinforcement learning model training. This process saves the Deep Q-Network weights on file **DQN.torch**
```
python3 rl_train.py
```

## Metrics analysis
```
python3 metric_run.py
```