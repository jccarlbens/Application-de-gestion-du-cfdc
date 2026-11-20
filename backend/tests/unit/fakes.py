"""Des doubles en mémoire de la DAL et de l'email, pour tester la BLL et les
routes sans base ni serveur d'email."""

import uuid
from dataclasses import replace
from datetime import UTC, datetime

from app.core.exceptions import DuplicateBadgeError, DuplicateEmailError, EmailDeliveryError, UserNotFoundError
from app.entities.ent_auth import EntLoginRecord, LoginOutcome
from app.entities.ent_user import EntActor, EntNewUser, EntUser, Role, TwoFactorChannel


class FakeEmail:
    def __init__(self, fails: bool = False) -> None:
        self.sent: list[dict] = []
        self._fails = fails

    def send(self, to: str, subject: str, body: str) -> None:
        if self._fails:
            raise EmailDeliveryError("L'email n'a pas pu être envoyé.")
        self.sent.append({"to": to, "subject": subject, "body": body})


class FakeDalUser:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, EntUser] = {}
        self.tokens: dict[str, dict] = {}
        self.password_hashes: dict[uuid.UUID, str] = {}
        self.failures_since: dict[uuid.UUID, datetime] = {}
        self.auth: "FakeDalAuth | None" = None  # pour fermer les sessions, comme la vraie DAL

    def create_user(self, new_user: EntNewUser, token_hash, token_expires_at, before_commit) -> EntUser:
        if any(u.badge == new_user.badge for u in self.users.values()):
            raise DuplicateBadgeError("Ce numéro de badge est déjà utilisé.")
        if any(u.email == new_user.email for u in self.users.values()):
            raise DuplicateEmailError("Cette adresse email est déjà utilisée.")
        user = EntUser(
            id=uuid.uuid4(),
            badge=new_user.badge,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            email=new_user.email,
            phone=new_user.phone,
            roles=new_user.roles,
            two_factor_channel=TwoFactorChannel.EMAIL,
            is_active=True,
            is_blocked=False,
            has_password=False,
            created_at=datetime.now(UTC),
        )
        before_commit(user)  # s'il échoue, rien n'est enregistré, comme la vraie DAL
        self.users[user.id] = user
        self.tokens[token_hash] = {"user_id": user.id, "expires_at": token_expires_at, "used": False}
        return user

    def get_user(self, user_id):
        if user_id not in self.users:
            raise UserNotFoundError("Ce compte n'existe pas.")
        return self.users[user_id]

    def list_users(self):
        return list(self.users.values())

    def count_active_admins(self) -> int:
        return sum(1 for u in self.users.values() if u.is_active and Role.IT_ADMIN in u.roles)

    def admin_exists(self) -> bool:
        return any(Role.IT_ADMIN in u.roles for u in self.users.values())

    def set_roles(self, user_id, roles):
        self.users[user_id] = replace(self.get_user(user_id), roles=roles)
        return self.users[user_id]

    def set_active(self, user_id, is_active, now=None):
        self.users[user_id] = replace(self.get_user(user_id), is_active=is_active)
        if not is_active and self.auth:
            self.auth.close_user_sessions(user_id)
        return self.users[user_id]

    def get_login_record(self, badge):
        user = next((u for u in self.users.values() if u.badge == badge), None)
        if user is None:
            return None
        return EntLoginRecord(user, self.password_hashes.get(user.id), self.failures_since.get(user.id))

    def get_user_by_badge(self, badge):
        user = next((u for u in self.users.values() if u.badge == badge), None)
        if user is None:
            raise UserNotFoundError("Aucun compte n'a ce numéro de badge.")
        return user

    def block(self, user_id, now) -> None:
        self.users[user_id] = replace(self.users[user_id], is_blocked=True)
        if self.auth:
            self.auth.close_user_sessions(user_id)

    def unblock(self, user_id, now):
        self.users[user_id] = replace(self.get_user(user_id), is_blocked=False)
        self.failures_since[user_id] = now
        return self.users[user_id]

    def add_user_with_password(self, badge: str, password_hash: str, roles=(Role.SECRETARY,)) -> EntUser:
        user = EntUser(
            id=uuid.uuid4(), badge=badge, first_name="Marie", last_name="Joseph", email=f"{badge}@example.test",
            phone=None, roles=frozenset(roles), two_factor_channel=TwoFactorChannel.EMAIL, is_active=True,
            is_blocked=False, has_password=True, created_at=datetime.now(UTC),
        )
        self.users[user.id] = user
        self.password_hashes[user.id] = password_hash
        return user


    def use_password_token(self, token_hash, password_hash, now) -> bool:
        token = self.tokens.get(token_hash)
        if token is None or token["used"] or token["expires_at"] <= now:
            return False
        token["used"] = True
        self.password_hashes[token["user_id"]] = password_hash
        user_id = token["user_id"]
        self.users[user_id] = replace(self.users[user_id], has_password=True)
        return True


def actor(*roles: Role) -> EntActor:
    return EntActor(user_id=uuid.uuid4(), roles=frozenset(roles))


class FakeDalAuth:
    def __init__(self) -> None:
        self.attempts: list[dict] = []
        self.sessions: dict[str, dict] = {}

    def record_attempt(self, badge_entered, user_id, outcome: LoginOutcome, now) -> None:
        self.attempts.append({"badge": badge_entered, "user_id": user_id, "outcome": outcome, "at": now})

    def consecutive_failures(self, user_id, counted_since) -> int:
        count = 0
        for attempt in reversed(self.attempts):
            if attempt["user_id"] != user_id:
                continue
            if attempt["outcome"] is LoginOutcome.SUCCESS or (counted_since and attempt["at"] <= counted_since):
                break
            count += 1
        return count

    def open_session(self, user_id, token_hash, now, expires_at) -> None:
        self.sessions[token_hash] = {"user_id": user_id, "expires_at": expires_at, "closed": False}

    def use_session(self, token_hash, now, new_expiry):
        session = self.sessions.get(token_hash)
        if session is None or session["closed"] or session["expires_at"] <= now:
            return None
        session["expires_at"] = new_expiry
        return session["user_id"]

    def close_session(self, token_hash, now) -> None:
        if token_hash in self.sessions:
            self.sessions[token_hash]["closed"] = True

    def close_user_sessions(self, user_id) -> None:
        for session in self.sessions.values():
            if session["user_id"] == user_id:
                session["closed"] = True


class FakeDalTraining:
    """Le catalogue en mémoire, avec la liste de départ (US-010)."""

    def __init__(self) -> None:
        self.domains: dict[uuid.UUID, dict] = {}
        self.subdomains: dict[uuid.UUID, dict] = {}
        self.trainings: dict[uuid.UUID, dict] = {}
        for domain, subs in (
            ("Sûreté-Sécurité", ("Sensibilisation sur la carte d'accès", "Conduite sur la rampe")),
            ("Accueil", ("Protocole", "Civilité")),
        ):
            domain_id = self.add_domain(domain).id
            for name in subs:
                self.add_subdomain(domain_id, name)

    def subdomain_id(self, name: str) -> uuid.UUID:
        return next(i for i, s in self.subdomains.items() if s["name"] == name)

    def domain_id(self, name: str) -> uuid.UUID:
        return next(i for i, d in self.domains.items() if d["name"] == name)

    def _domain(self, domain_id):
        from app.entities.ent_training import EntDomain, EntSubdomain

        subs = sorted(
            (EntSubdomain(i, s["domain_id"], s["name"]) for i, s in self.subdomains.items() if s["domain_id"] == domain_id),
            key=lambda s: s.name.casefold(),
        )
        return EntDomain(domain_id, self.domains[domain_id]["name"], tuple(subs))

    def list_domains(self):
        return sorted((self._domain(i) for i in self.domains), key=lambda d: d.name.casefold())

    def add_domain(self, name):
        domain_id = uuid.uuid4()
        self.domains[domain_id] = {"name": name}
        return self._domain(domain_id)

    def rename_domain(self, domain_id, name):
        self.domains[domain_id]["name"] = name
        return self._domain(domain_id)

    def add_subdomain(self, domain_id, name):
        from app.entities.ent_training import EntSubdomain

        sub_id = uuid.uuid4()
        self.subdomains[sub_id] = {"domain_id": domain_id, "name": name}
        return EntSubdomain(sub_id, domain_id, name)

    def rename_subdomain(self, subdomain_id, name):
        from app.entities.ent_training import EntSubdomain

        self.subdomains[subdomain_id]["name"] = name
        return EntSubdomain(subdomain_id, self.subdomains[subdomain_id]["domain_id"], name)

    def subdomain_exists(self, subdomain_id) -> bool:
        return subdomain_id in self.subdomains

    def _training(self, training_id):
        from app.entities.ent_training import EntTraining

        t = self.trainings[training_id]
        sub = self.subdomains[t["subdomain_id"]]
        return EntTraining(
            training_id, t["title"], t["description"], t["subdomain_id"], sub["name"],
            sub["domain_id"], self.domains[sub["domain_id"]]["name"], datetime(2026, 11, 20, tzinfo=UTC),
        )

    def list_trainings(self):
        return [self._training(i) for i in self.trainings]

    def get_training(self, training_id):
        from app.core.exceptions import RecordNotFoundError

        if training_id not in self.trainings:
            raise RecordNotFoundError("Cette formation n'existe pas.")
        return self._training(training_id)

    def _check_unique(self, key, ignore=None) -> None:
        from app.core.exceptions import DuplicateNameError

        if any(t["title_key"] == key for i, t in self.trainings.items() if i != ignore):
            raise DuplicateNameError("Une formation porte déjà cet intitulé.")

    def create_training(self, training):
        self._check_unique(training.title_key)
        training_id = uuid.uuid4()
        self.trainings[training_id] = dict(training.__dict__)
        return self._training(training_id)

    def update_training(self, training_id, training):
        self._check_unique(training.title_key, ignore=training_id)
        self.trainings[training_id] = dict(training.__dict__)
        return self._training(training_id)

    # --- Modules et formateurs (US-011) ---------------------------------------

    def add_trainer(self, first: str, last: str, badge: str, is_active=True, is_trainer=True):
        from app.entities.ent_training import EntTrainer

        trainer = EntTrainer(uuid.uuid4(), first, last, badge, is_active, is_trainer)
        self.trainers = {**getattr(self, "trainers", {}), trainer.id: trainer}
        return trainer

    def training_exists(self, training_id) -> bool:
        return training_id in self.trainings

    def _module(self, module_id):
        from app.entities.ent_training import EntModule

        m = self.modules[module_id]
        trainer = getattr(self, "trainers", {}).get(m["trainer_id"]) if m["trainer_id"] else None
        return EntModule(module_id, m["training_id"], m["title"], m["description"], trainer, m["created_at"])

    def list_modules(self, training_id):
        return [self._module(i) for i, m in getattr(self, "modules", {}).items() if m["training_id"] == training_id]

    def get_module(self, module_id):
        from app.core.exceptions import RecordNotFoundError

        if module_id not in getattr(self, "modules", {}):
            raise RecordNotFoundError("Ce module n'existe pas.")
        return self._module(module_id)

    def _check_module_title(self, training_id, key, ignore=None) -> None:
        from app.core.exceptions import DuplicateNameError

        for i, m in getattr(self, "modules", {}).items():
            if i != ignore and m["training_id"] == training_id and m["title_key"] == key:
                raise DuplicateNameError("Cette formation a déjà un module de ce titre.")

    def add_module(self, training_id, module):
        self.modules = getattr(self, "modules", {})
        self._check_module_title(training_id, module.title_key)
        module_id = uuid.uuid4()
        self.modules[module_id] = {
            **module.__dict__,
            "training_id": training_id,
            "created_at": datetime(2026, 11, 20, tzinfo=UTC),
        }
        return self._module(module_id)

    def update_module(self, module_id, module):
        current = self.modules[module_id]
        self._check_module_title(current["training_id"], module.title_key, ignore=module_id)
        self.modules[module_id] = {**current, **module.__dict__}
        return self._module(module_id)

    def get_trainer(self, user_id):
        return getattr(self, "trainers", {}).get(user_id)

    def list_active_trainers(self):
        return sorted(
            (t for t in getattr(self, "trainers", {}).values() if t.is_active and t.is_trainer),
            key=lambda t: (t.last_name, t.first_name),
        )

    def list_trainer_modules(self, trainer_id):
        pairs = [
            (self._training(m["training_id"]), self._module(i))
            for i, m in getattr(self, "modules", {}).items()
            if m["trainer_id"] == trainer_id
        ]
        return sorted(pairs, key=lambda p: p[0].title)
