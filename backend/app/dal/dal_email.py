import smtplib
from email.message import EmailMessage

import structlog

from app.core.config import settings
from app.core.exceptions import EmailDeliveryError

logger = structlog.get_logger(__name__)


class DalEmail:
    """Envoie un email par SMTP : Mailpit en local, Brevo sur le serveur de
    test. Le fournisseur se choisit par la configuration (ADR 4)."""

    def send(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = settings.email_sender
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
                if settings.smtp_starttls:
                    smtp.starttls()
                if settings.smtp_username:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            # Jamais l'adresse dans les journaux : une donnée personnelle.
            logger.error("email_delivery_failed", error_type=type(error).__name__)
            raise EmailDeliveryError(
                "L'email n'a pas pu être envoyé. Réessayez plus tard ou prévenez l'administrateur."
            ) from error
