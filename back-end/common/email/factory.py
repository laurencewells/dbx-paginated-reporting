"""Resolves the correct EmailProvider from a SmtpConnection record.

The factory is the only place that knows about the provider enum values and
the secret store. Providers themselves receive plain credentials.
"""
from common.email._secret import get_secret
from common.email.base import EmailProvider


def get_provider(connection) -> EmailProvider:
    """Return the EmailProvider for the given SmtpConnection.

    Args:
        connection: A SmtpConnection model instance.

    Returns:
        A ready-to-use EmailProvider.
    """
    credential = get_secret(connection.secret_scope, connection.secret_key)

    if connection.provider == "sendgrid":
        from common.email.providers.sendgrid import SendGridEmailProvider
        return SendGridEmailProvider(api_key=credential)

    from common.email.providers.smtp import SmtpEmailProvider
    return SmtpEmailProvider(
        host=connection.smtp_host,
        port=connection.smtp_port,
        username=connection.username,
        password=credential,
    )
