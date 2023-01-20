from src.path_finding import PathFindingRunner, Heuristics
from src.metrics import Analyzer
from src.path_finding.astar import AStar
from src.path_finding.greedy import Greedy
from src.rl import RLRunner
from src.rule_based.rule_based_runner import RuleBasedRunner

analyzer = Analyzer(
    algorithms=[
        RuleBasedRunner(),
        PathFindingRunner(algorithm=Greedy()),
        PathFindingRunner(algorithm=Greedy(heuristic=Heuristics.manhattan)),
        PathFindingRunner(algorithm=Greedy(heuristic=Heuristics.euclidean)),
        PathFindingRunner(algorithm=Greedy(heuristic=Heuristics.walkable_steps_in_matrix)),
        PathFindingRunner(algorithm=AStar()),
        PathFindingRunner(algorithm=AStar(heuristic=Heuristics.manhattan)),
        PathFindingRunner(algorithm=AStar(heuristic=Heuristics.euclidean)),
        PathFindingRunner(algorithm=AStar(heuristic=Heuristics.walkable_steps_in_matrix)),
        # RLRunner(),
    ],
    env_n=15,
    max_episode_steps=1000,
)

analyzer.analyze()

analyzer.to_csv()
