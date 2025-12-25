import keyring
from keyring.errors import (
    NoKeyringError,
    KeyringLocked,
    PasswordSetError,
    PasswordDeleteError,
)

SERVICE_NAME = "tuitable"


def fallback_save_token(token: str, token_type: str = "pat"):
    pass


def fallback_get_token(token_type: str = "pat"):
    pass


def fallback_delete_token(token: str, token_type: str = "pat"):
    pass


def save_token(token: str, token_type: str = "access") -> dict[str, str] | None:
    try:
        keyring.set_password(SERVICE_NAME, f"auth_{token_type}", token)
    except (NoKeyringError, KeyringLocked, PasswordDeleteError, PasswordSetError) as e:
        return {"error": type(e).__name__}


def get_token(token_type: str = "access") -> str | dict[str, str] | None:
    try:
        return keyring.get_password(SERVICE_NAME, f"auth_{token_type}")
    except (NoKeyringError, KeyringLocked, PasswordDeleteError, PasswordSetError) as e:
        return {"error": type(e).__name__}


def delete_token(token_type: str = "access"):
    try:
        keyring.delete_password(SERVICE_NAME, f"auth_{token_type}")
    except (NoKeyringError, KeyringLocked, PasswordDeleteError, PasswordSetError) as e:
        return {"error": type(e).__name__}
