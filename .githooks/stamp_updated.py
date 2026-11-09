"""Estampille `updated:` sur chaque fichier markdown indexé, en UTC.

Lancé depuis .githooks/pre-commit. L'idée est qu'`updated:` est un fait que git
possède déjà, donc personne ne devrait avoir à s'en souvenir : l'alternative
était une date maintenue à la main, et ce dépôt a déjà vu trois documents
porter un décompte de tests obsolète pendant deux Epics.

Deux choses qu'il refuse délibérément de faire :

* Il n'estampille pas un fichier comportant des modifications non indexées.
  Réindexer un tel fichier emporterait ces modifications dans le commit à
  l'insu de l'auteur, ce qui est pire qu'une date obsolète. Il avertit et le
  saute à la place.
* Il n'invente pas de `created:`. Un fichier sans frontmatter reçoit un bloc
  complet avec les deux dates égales ; un fichier dont le frontmatter n'a pas
  de `created:` le reçoit avec la même valeur qu'`updated:`, ce qui est la
  meilleure estimation disponible et se voit comme une estimation, puisque les
  deux coïncident.
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Sous Windows, la sortie standard de Python prend par défaut l'encodage ANSI
# du système, et un accent sorti ainsi s'affiche en caractère de remplacement
# dans un terminal qui attend de l'UTF-8. Les messages de ce script sont en
# français, donc on force le flux plutôt que de retirer les accents.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def staged_markdown() -> list[str]:
    # ACMR, et non ACM. Le R est porteur : git signale un renommage par R, donc
    # la première version de ce hook sautait en silence chaque fichier renommé
    # - et le commit qui a installé le hook renommait onze documents, dont il a
    # refusé d'estampiller les onze tout en annonçant un succès sur les
    # soixante-quatre autres.
    out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "--", "*.md")
    return [line for line in out.splitlines() if line.strip()]


def has_unstaged_changes(path: str) -> bool:
    return bool(git("diff", "--name-only", "--", path).strip())


def stamp(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        block = f"---\ncreated: {NOW}\nupdated: {NOW}\n---\n\n"
        path.write_text(block + text, encoding="utf-8")
        return "frontmatter ajouté"

    end = text.find("\n---", 3)
    if end == -1:
        return "SAUTÉ - le frontmatter s'ouvre et ne se referme jamais"

    head, rest = text[: end + 1], text[end + 1 :]

    if re.search(r"^updated:", head, re.M):
        new_head = re.sub(r"^updated:.*$", f"updated: {NOW}", head, count=1, flags=re.M)
    else:
        new_head = head.rstrip("\r\n") + f"\nupdated: {NOW}\n"

    if not re.search(r"^created:", new_head, re.M):
        new_head = re.sub(r"^updated:", f"created: {NOW}\nupdated:", new_head, count=1, flags=re.M)

    if new_head == head:
        return "inchangé"
    path.write_text(new_head + rest, encoding="utf-8")
    return "estampillé"


def main() -> int:
    files = staged_markdown()
    if not files:
        return 0

    restaged, skipped = [], []
    for name in files:
        path = Path(name)
        if not path.exists():
            continue
        if has_unstaged_changes(name):
            skipped.append(name)
            continue
        result = stamp(path)
        if result in ("estampillé", "frontmatter ajouté"):
            restaged.append(name)
        elif result.startswith("SAUTÉ"):
            print(f"  {name}: {result}", file=sys.stderr)

    if restaged:
        subprocess.run(["git", "add", "--", *restaged], check=True)
        print(f"updated: {NOW} estampillé sur {len(restaged)} fichier(s)")

    for name in skipped:
        print(f"  non estampillé, il a des modifications non indexées : {name}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
