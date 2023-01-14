from src.minihack.env import Env


class AlgorithmRunner:
    def init_env(self, env: Env) -> None:
        """
        Environment initializer.
        :param env: Environment
        :return: None
        """
        pass

    def run(self) -> tuple[bool, float, float, float, float]:
        """
        Algorithm run function
        :return: Tuple composed by:
        0: flag that is true if match is winned
        1: total steps
        2: steps to reach the first key
        3: steps to reach the first door
        4: steps to reach the first corridor
        """
        pass
