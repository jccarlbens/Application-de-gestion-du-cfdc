from dataclasses import dataclass


@dataclass(frozen=True)
class EntHealth:
    """L'état du service : il répond, et sait-il joindre sa base ?"""

    is_database_reachable: bool
