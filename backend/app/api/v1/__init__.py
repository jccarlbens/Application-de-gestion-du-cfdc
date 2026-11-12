from fastapi import APIRouter

from app.api.v1 import health

router = APIRouter()

# Le routeur de chaque ressource s'ajoute ici à mesure qu'il est construit.
router.include_router(health.router)
