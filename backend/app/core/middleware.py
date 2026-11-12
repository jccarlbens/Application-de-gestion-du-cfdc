import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger(__name__)


class HTTPRequestContextMiddleware(BaseHTTPMiddleware):
    """Enveloppe chaque requête HTTP que ce service traite. Fait quatre
    choses :

    1. Corrélation des requêtes — génère un request_id (UUID) par requête et
       le lie aux contextvars de structlog, de sorte que chaque ligne de
       journal émise n'importe où pendant le traitement de cette requête
       (DAL, BLL, api/, et même la ligne de journal d'accès d'uvicorn) porte
       automatiquement le même request_id, sans aucun passage explicite.
    2. Observabilité automatique au niveau de la requête — journalise
       request_started et request_finished en INFO pour chaque point
       d'entrée (méthode, chemin, status_code, duration_ms), sans aucun code
       de journalisation par route.
    3. En-tête de réponse X-Request-ID — renvoie le même identifiant à
       l'appelant, pour qu'une réponse HTTP puisse plus tard être rapprochée
       de ses lignes de journal exactes.
    4. Filet de sécurité d'exception en dernier recours — journalise en
       CRITICAL, avec la trace complète, tout ce qui atteint ce try/except,
       puis relève l'exception. app.add_middleware() enveloppe le système de
       gestionnaires d'exceptions de FastAPI, donc ceci n'attrape jamais que
       des exceptions sans gestionnaire enregistré — de vrais bogues
       inattendus, jamais une exception de domaine connue, que
       core/exception_handlers.py a déjà attrapée avant que ceci ne
       s'exécute.

    Nommé explicitement « HTTP » parce que BaseHTTPMiddleware ne traite que
    le type de scope ASGI « http » — il ne s'exécute jamais pour une
    connexion WebSocket. Un futur point d'entrée WebSocket aurait besoin de
    son propre middleware ASGI pur pour la même corrélation de request_id ;
    il ne l'obtiendrait pas de cette classe.
    """

    async def dispatch(self, request: Request, call_next):
        structlog.contextvars.clear_contextvars()
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        logger.info("request_started", method=request.method, path=request.url.path)
        try:
            response = await call_next(request)
        except Exception:
            logger.critical("request_failed", method=request.method, path=request.url.path, exc_info=True)
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request_finished",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        response.headers["X-Request-ID"] = request_id
        return response
