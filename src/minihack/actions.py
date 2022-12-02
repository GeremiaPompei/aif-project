from nle import nethack

MOVE_ACTIONS = tuple(nethack.CompassDirection)
ACTIONS = MOVE_ACTIONS + (
    nethack.Command.OPEN,
    nethack.Command.KICK,
    nethack.Command.SEARCH,
)
