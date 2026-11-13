"""Commandes de l'administrateur informatique, lancées sur le serveur ou
depuis son poste avec l'adresse de la base (US-002).

    uv run python -m app.cli create-admin --badge A01-01 --first-name P --last-name N --email E [--phone T]
    uv run python -m app.cli create-user  --badge B07-42 --first-name P --last-name N --email E \\
        --role secretary [--role trainer …] [--phone T]

Chacune envoie à la personne un lien pour choisir son mot de passe. La base
visée est celle de `DATABASE_URL` ; la procédure est dans backend/README.md.
"""

import argparse
import sys

from app.bll.bll_user import AccountInput, BllUser
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.entities.ent_user import Role

EXIT_OK = 0
EXIT_FAILED = 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="Comptes du CFDC (US-002).")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("create-admin", "Crée le premier administrateur informatique (une seule fois)."),
        ("create-user", "Crée un compte avec un ou plusieurs rôles."),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--badge", required=True, help="Numéro de badge AAN, par exemple A01-01.")
        command.add_argument("--first-name", required=True)
        command.add_argument("--last-name", required=True)
        command.add_argument("--email", required=True)
        command.add_argument("--phone")
        if name == "create-user":
            command.add_argument(
                "--role",
                action="append",
                required=True,
                choices=[role.value for role in Role],
                help="Rôle du compte ; répétez l'option pour en donner plusieurs.",
            )
    return parser


def main(argv: list[str] | None = None, bll: BllUser | None = None) -> int:
    args = _parser().parse_args(argv)
    configure_logging(settings.log_level, settings.environment)
    bll = bll or BllUser()
    roles = args.role if args.command == "create-user" else [Role.IT_ADMIN.value]
    account = AccountInput(args.badge, args.first_name, args.last_name, args.email, args.phone, roles)
    try:
        if args.command == "create-admin":
            user = bll.create_first_admin(account)
        else:
            user = bll.create_user(None, account)
    except AppError as error:
        print(f"Échec : {error}", file=sys.stderr)
        return EXIT_FAILED
    roles_text = ", ".join(sorted(role.value for role in user.roles))
    print(f"Compte créé : {user.badge} ({user.first_name} {user.last_name}), rôles : {roles_text}.")
    print("Un lien pour choisir le mot de passe a été envoyé par email.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
