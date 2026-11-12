"""Mise en place de la journalisation structurée (structlog par-dessus la
bibliothèque standard).

Le modèle de journalisation de la bibliothèque standard de Python a 5
sévérités réelles : CRITICAL, ERROR, WARNING, INFO, DEBUG. « FATAL » et
« WARN » ne sont pas des niveaux distincts — ce sont de simples alias que la
bibliothèque standard définit elle-même pour CRITICAL et WARNING (même valeur
entière). « TRACE » n'existe pas du tout dans la bibliothèque standard ; il
est enregistré ici, en dessous de DEBUG.

Correspondance au point d'appel pour les six niveaux demandés :
    TRACE (5)     -> logger.log(TRACE, "event_name", **kw)
    DEBUG (10)    -> logger.debug("event_name", **kw)
    INFO (20)     -> logger.info("event_name", **kw)
    WARN (30)     -> logger.warning("event_name", **kw)   -- « warn » est un alias déprécié, ne l'employez pas
    ERROR (40)    -> logger.error("event_name", **kw)
    FATAL (50)    -> logger.critical("event_name", **kw)  -- « fatal » est un alias déprécié, ne l'employez pas

Ne passez jamais une donnée personnelle brute comme champ de journal —
journalisez un identifiant à la place. Vérifiez les engagements de
conservation et de suppression des données propres à ce service avant de
supposer que c'est couvert.
"""

import logging
import sys

import structlog

TRACE = 5
logging.addLevelName(TRACE, "TRACE")


def configure_logging(log_level: str, environment: str) -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    renderer = (
        structlog.dev.ConsoleRenderer()
        if environment == "development"
        else structlog.processors.JSONRenderer()
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # Fait passer les enregistrements de journal d'uvicorn par le même
    # gestionnaire et le même format, au lieu de la configuration par défaut
    # d'uvicorn, pour que tout forme un seul flux cohérent.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = []
        uv_logger.propagate = True
