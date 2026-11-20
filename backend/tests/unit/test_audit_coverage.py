"""Une table oubliée par le journal ne doit pas passer inaperçue (US-003) :
chaque table est journalisée (`__audit__`) ou exemptée, avec sa raison, dans
`EXEMPT_TABLES`. Ce test échoue dès qu'un Epic ajoute une table sans choisir."""

import importlib
import pkgutil

import app.dal
from app.dal.dal_audit import EXEMPT_TABLES
from app.dal.database import Base

# Toutes les tables existent seulement une fois tous les modules de la DAL importés.
for module in pkgutil.iter_modules(app.dal.__path__):
    importlib.import_module(f"app.dal.{module.name}")

AUDITED = {
    mapper.class_.__tablename__
    for mapper in Base.registry.mappers
    if getattr(mapper.class_, "__audit__", None) is not None
}


def test_every_table_is_audited_or_exempted() -> None:
    forgotten = set(Base.metadata.tables) - AUDITED - set(EXEMPT_TABLES)
    assert forgotten == set(), f"Tables ni journalisées ni exemptées : {sorted(forgotten)}"


def test_no_table_is_both_audited_and_exempted() -> None:
    assert AUDITED & set(EXEMPT_TABLES) == set()


def test_accounts_and_their_roles_are_audited() -> None:
    assert {"users", "user_roles"} <= AUDITED


def test_every_exemption_gives_its_reason() -> None:
    assert all(reason.strip() for reason in EXEMPT_TABLES.values())


def test_the_catalogue_tables_are_audited() -> None:
    assert {"domains", "subdomains", "trainings"} <= AUDITED
