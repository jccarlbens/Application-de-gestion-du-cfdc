from fastapi import FastAPI


def register_exception_handlers(app: FastAPI) -> None:
    """Enregistre un @app.exception_handler(...) par exception de niveau
    métier de core/exceptions.py qui doit correspondre à un statut HTTP
    précis. C'est le SEUL endroit qui traduit une exception de domaine en
    réponse HTTP — les routeurs de api/ ne font jamais de try/except pour
    cela.

    Exemple travaillé, une fois qu'une vraie exception métier existe :

        @app.exception_handler(DuplicateEmailError)
        async def handle_duplicate_email(request, exc):
            return JSONResponse(status_code=409, content={"detail": "..."})
    """
