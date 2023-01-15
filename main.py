from src.minihack.env import Env
from src.path_finding.astar_runner import AStarRunner
from src.metrics import Analyzer
from src.path_finding.heuristics import Heuristics
from src.rule_based.rule_based_runner import RuleBasedRunner

"""
analyzer = Analyzer(
    algorithms=[
        AStarRunner(),
        AStarRunner(heuristic=Heuristics.manhattan),
        AStarRunner(heuristic=Heuristics.euclidean),
        AStarRunner(heuristic=Heuristics.walkable_steps_in_matrix),
    ],
    env_n=3,
    max_episode_steps=1000,
)

analyzer.analyze()

print(analyzer.metrics)
"""

rbr = RuleBasedRunner(Env(max_episode_steps = 1000))

rbr.run()