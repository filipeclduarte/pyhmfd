"""Credential resolution: env vars → keyring → interactive prompt."""

from __future__ import annotations

import getpass
import os
import sys


def _try_keyring(service: str, username: str) -> str | None:
    try:
        import keyring

        return keyring.get_password(service, username)
    except Exception:
        return None


def _store_keyring(service: str, username: str, password: str) -> None:
    try:
        import keyring

        keyring.set_password(service, username, password)
    except Exception:
        pass


def resolve_credentials(
    username: str | None,
    password: str | None,
    *,
    service: str,
    env_user: str,
    env_pass: str,
) -> tuple[str, str]:
    """Return (username, password), sourcing from env vars, keyring, or prompt.

    Resolution order for each value: argument → env var → keyring → prompt.
    Credentials obtained interactively are offered to keyring for storage.
    """
    username = username or os.environ.get(env_user)
    password = password or os.environ.get(env_pass)

    if username and not password:
        password = _try_keyring(service, username)

    if not username:
        if not sys.stdin.isatty():
            raise ValueError(
                f"No username supplied. Set the {env_user} environment variable "
                f"or pass username= explicitly."
            )
        username = input(f"Enter {service} username (email): ").strip()

    if not password:
        if not sys.stdin.isatty():
            raise ValueError(
                f"No password supplied. Set the {env_pass} environment variable "
                f"or pass password= explicitly."
            )
        password = getpass.getpass(f"Enter {service} password: ")
        _store_keyring(service, username, password)

    return username, password
