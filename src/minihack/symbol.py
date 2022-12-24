from src.minihack.color import Colors


class Symbol:
    def __init__(self, char, color):
        self.char = char if str(char).isnumeric() else ord(char)
        self.color = color if str(color).isnumeric() else Colors.COLORS[color]

    def __hash__(self):
        return hash((self.char, self.color))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        return f"Symbol({chr(self.char)}, {Colors.COLORS_NUMS[self.color]}))"


class Symbols:
    HERO_CHAR = Symbol('@', 15)
    WALL_CHARS = [Symbol('-', Colors.WHITE), Symbol('|', Colors.WHITE)]
    KEY_CHAR = Symbol('(', Colors.CYAN)
    DOOR_OPEN_CHARS = [Symbol('-', Colors.YELLOW), Symbol('|', Colors.YELLOW)]
    DOOR_CLOSE_CHARS = [Symbol('+', Colors.YELLOW)]
    STAIR_UP_CHAR = Symbol('>', Colors.WHITE)
    STAIR_DOWN_UP = Symbol('<', Colors.WHITE)
    FLOOR_CHAR = Symbol('.', Colors.WHITE)
    CORRIDOR_CHARS = [Symbol('#', Colors.WHITE), Symbol('`', Colors.WHITE)]
    OBSCURE_CHAR = Symbol(' ', Colors.BLACK)

    TOTAL_SYMBOLS = WALL_CHARS + DOOR_OPEN_CHARS + DOOR_CLOSE_CHARS + CORRIDOR_CHARS + \
                    [FLOOR_CHAR, HERO_CHAR, KEY_CHAR, STAIR_UP_CHAR, STAIR_DOWN_UP, OBSCURE_CHAR]

    @staticmethod
    def get_symbol_from_env(env, symbol):
        if symbol.color in env.obs['chars'] and symbol.char in env.obs['colors']:
            return symbol
        return None
