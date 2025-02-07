from typing import Iterator, Awaitable, Callable
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager
import json

import aiofiles
from aiohttp import ClientSession

from simplipy import API
from simplipy.util.auth import (
    get_auth0_code_challenge,
    get_auth0_code_verifier,
    get_auth_url,
)


class Token(str):
    @classmethod
    async def async_load(cls, path: str):
        async with aiofiles.open(path, mode="r") as f:
            return cls(json.loads(await f.read()))

    async def async_save(self, path: str):
        async with aiofiles.open(path, mode="w") as f:
            await f.write(json.dumps(self))


@contextmanager
def auth_flow() -> Iterator[tuple[str, Callable[[str], Awaitable[Token]]]]:
    """
    Context manager for SimpliSafe authentication.
    Yields:
        auth_url (str): The URL the user needs to visit.
        verify_code (Callable[[str], Awaitable[str]]): Function to verify the auth code and get the refresh token.
    """

    code_verifier = get_auth0_code_verifier()
    code_challenge = get_auth0_code_challenge(code_verifier)
    auth_url = get_auth_url(code_challenge)

    async def verify_code(auth_code: str) -> Token:
        """
        Verifies the auth code and returns the refresh token.
        Args:
            auth_code (str): The authorization code.
        Returns:
            refresh_token (str): The refresh token.
        """

        if auth_code.startswith("com.simplisafe.mobile://"):
            # If the user provides the full redirect URL, extract the authorization code
            # from it:
            if not (auth_code := parse_qs(urlparse(auth_code).query).get("code", [""])[0]):
                raise ValueError("Invalid authorization code provided.")

        if auth_code.startswith("="):
            # strip the "=" from the URL query params
            auth_code = auth_code[1:]

        if len(auth_code) != 45:
            # SimpliSafe authorization codes are 45 characters in length
            raise ValueError(f"Invalid authorization code provided: {auth_code}")

        """Create the aiohttp session and run."""
        async with ClientSession() as session:
            simplisafe = await API.async_from_auth(
                auth_code,
                code_verifier,
                session=session,
            )
            return Token(simplisafe.refresh_token)

    yield auth_url, verify_code
