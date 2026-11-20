from fastapi import APIRouter

from app.api.v1 import auth, health, history, password, trainings, users

router = APIRouter()

# Le routeur de chaque ressource s'ajoute ici à mesure qu'il est construit.
router.include_router(health.router)
router.include_router(users.router)
router.include_router(password.router)
router.include_router(history.router)
router.include_router(auth.router)
router.include_router(trainings.router)
