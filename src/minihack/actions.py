from nle import nethack

MOVE_ACTIONS = tuple(nethack.CompassDirection)
ACTIONS = [
    nethack.CompassCardinalDirection.N,
    nethack.CompassCardinalDirection.E,
    nethack.CompassCardinalDirection.S,
    nethack.CompassCardinalDirection.W,
    nethack.Command.APPLY,
]

ACTIONS_DICT = {action: i for i, action in enumerate(ACTIONS)}
