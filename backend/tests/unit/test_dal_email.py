import smtplib

import pytest

from app.core.config import settings
from app.core.exceptions import EmailDeliveryError
from app.dal import dal_email
from app.dal.dal_email import DalEmail


class _FakeSMTP:
    instances: list["_FakeSMTP"] = []

    def __init__(self, host, port, timeout) -> None:
        self.host, self.port = host, port
        self.calls: list[str] = []
        self.message = None
        _FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        pass

    def starttls(self) -> None:
        self.calls.append("starttls")

    def login(self, user, password) -> None:
        self.calls.append(f"login:{user}")

    def send_message(self, message) -> None:
        self.message = message


@pytest.fixture(autouse=True)
def fake_smtp(monkeypatch):
    _FakeSMTP.instances.clear()
    monkeypatch.setattr(dal_email.smtplib, "SMTP", _FakeSMTP)


def test_sends_through_the_configured_server(monkeypatch) -> None:
    monkeypatch.setattr(settings, "smtp_host", "smtp-relay.example.test")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_starttls", True)
    monkeypatch.setattr(settings, "smtp_username", "cfdc")

    DalEmail().send("marie@example.test", "Sujet", "Corps")

    smtp = _FakeSMTP.instances[0]
    assert (smtp.host, smtp.port) == ("smtp-relay.example.test", 587)
    assert smtp.calls == ["starttls", "login:cfdc"]
    assert smtp.message["To"] == "marie@example.test"


def test_mailpit_needs_neither_tls_nor_login(monkeypatch) -> None:
    monkeypatch.setattr(settings, "smtp_starttls", False)
    monkeypatch.setattr(settings, "smtp_username", "")
    DalEmail().send("marie@example.test", "Sujet", "Corps")
    assert _FakeSMTP.instances[0].calls == []


def test_a_refusing_server_becomes_a_french_error(monkeypatch) -> None:
    class _Refusing(_FakeSMTP):
        def send_message(self, message) -> None:
            raise smtplib.SMTPRecipientsRefused({})

    monkeypatch.setattr(dal_email.smtplib, "SMTP", _Refusing)
    with pytest.raises(EmailDeliveryError, match="n'a pas pu être envoyé"):
        DalEmail().send("marie@example.test", "Sujet", "Corps")
