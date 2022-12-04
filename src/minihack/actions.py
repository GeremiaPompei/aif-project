from nle import nethack

MOVE_ACTIONS = tuple(nethack.CompassDirection)
ACTIONS = [
    nethack.CompassCardinalDirection.N,
    nethack.CompassCardinalDirection.S,
    nethack.CompassCardinalDirection.E,
    nethack.CompassCardinalDirection.W,
    nethack.CompassIntercardinalDirection.NW,
    nethack.CompassIntercardinalDirection.NE,
    nethack.CompassIntercardinalDirection.SW,
    nethack.CompassIntercardinalDirection.SE,
    nethack.Command.PICKUP,
    nethack.Command.OPEN,
    nethack.Command.KICK,
    nethack.Command.SEARCH,
]

ACTIONS_DICT = {action: i for i, action in enumerate(ACTIONS)}
