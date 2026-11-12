from fastapi import FastAPI

from app.api import v1
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import HTTPRequestContextMiddleware

configure_logging(settings.log_level, settings.environment)

app = FastAPI(title="CFDC — API")
app.add_middleware(HTTPRequestContextMiddleware)
register_exception_handlers(app)

app.include_router(v1.router, prefix="/api/v1")

# Si un frontend de navigateur servi depuis une autre origine doit appeler ce
# service, ajoutez CORSMiddleware ici dès maintenant, avec la ou les origines
# autorisées sous forme de champ Settings — et non codées en dur. Une
# vérification par curl ne peut pas détecter une configuration CORS
# manquante ; seul un contrôle depuis un vrai navigateur peut le faire. Voir
# project-docs/learnings/03-backend-layered-architecture-template.md.
