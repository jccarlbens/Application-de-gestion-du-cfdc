"""Les routes réelles de l'API, préfixe compris. Depuis FastAPI 0.16x, un
routeur inclus apparaît dans `app.routes` comme un seul objet : il faut
demander ses routes effectives, sinon un test qui parcourt les routes n'en
trouve aucune et passe sans rien vérifier."""

from dataclasses import dataclass

from app.main import app


@dataclass(frozen=True)
class ApiRoute:
    path: str
    methods: frozenset[str]
    dependant: object


def api_routes(prefix: str = "/api/v1") -> list[ApiRoute]:
    found: list[ApiRoute] = []
    for route in app.routes:
        contexts = route.effective_route_contexts() if hasattr(route, "effective_route_contexts") else [route]
        for ctx in contexts:
            path = getattr(ctx, "path", "")
            dependant = getattr(ctx, "dependant", None)
            if path.startswith(prefix) and dependant is not None:
                found.append(ApiRoute(path, frozenset(ctx.methods or ()), dependant))
    return found
