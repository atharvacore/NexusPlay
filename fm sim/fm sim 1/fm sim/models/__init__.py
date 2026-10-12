from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .club import Club  # noqa: E402,F401
from .player import Player  # noqa: E402,F401
from .manager import Manager  # noqa: E402,F401
from .season import Season, Fixture, Standing  # noqa: E402,F401
from .transfer import Transfer, Contract, Bid  # noqa: E402,F401
from .match import Match, MatchEvent  # noqa: E402,F401
from .inbox import InboxMessage  # noqa: E402,F401
from .tactics import TacticsSetup  # noqa: E402,F401
from .game_state import GameState  # noqa: E402,F401
