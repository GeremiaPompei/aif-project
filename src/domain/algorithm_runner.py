from src.minihack.env import Env
from src.minihack.symbol import Symbols


class AlgorithmRunner:
    def __init__(self):
        self.total_steps = 0
        self.steps_first_key = None
        self.steps_first_door = None
        self.steps_first_corridor = None
        self.win = None
        self.env = None

    def init_env(self, env: Env) -> None:
        """
        Environment initializer.
        :param env: Environment
        :return: None
        """
        self.env = env
        self.total_steps = 0
        self.steps_first_key = None
        self.steps_first_door = None
        self.steps_first_corridor = None
        self.win = None
        self.env.step_callback = self.one_more_step

    def one_more_step(self):
        if self.env.done:
            self.win = self.env.over_hero_symbol == Symbols.STAIR_UP_CHAR
        else:
            self.total_steps += 1
            if self.steps_first_key is None and self.env.over_hero_symbol == Symbols.KEY_CHAR:
                self.steps_first_key = self.total_steps
            if self.steps_first_door is None and self.env.over_hero_symbol in Symbols.DOOR_OPEN_CHARS + Symbols.DOOR_CLOSE_CHARS:
                self.steps_first_door = self.total_steps
            if self.steps_first_corridor is None and self.env.over_hero_symbol in Symbols.CORRIDOR_CHARS:
                self.steps_first_corridor = self.total_steps

    def run(self):
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
