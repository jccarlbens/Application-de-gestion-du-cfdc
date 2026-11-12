from app.dal.dal_health import DalHealth
from app.entities.ent_health import EntHealth


class BllHealth:
    def __init__(self, dal: DalHealth | None = None) -> None:
        self._dal = dal or DalHealth()

    def get_health(self) -> EntHealth:
        return EntHealth(is_database_reachable=self._dal.is_database_reachable())
