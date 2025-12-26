import asyncio
import base64
import hashlib
import secrets
import webbrowser

import httpx
from aiohttp import web
from requests import Request
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Middle
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Label

from ..util.credentials import get_token


class OverviewScreen(Screen[str]):
    CSS_PATH = "overview.tcss"

    def __init__(self, token: str):
        self.token = token
        super().__init__()

    async def on_mount(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.airtable.com/v0/meta/bases",
                headers={"Authorization": f"Bearer: {self.token}"},
            )

    def compose(self) -> ComposeResult: ...

    ...


class BaseWidget(Widget):
    def __init__(self, base_id: str, base_name: str, base_perms: str) -> None:
        self.base_id = base_id
        self.base_name = base_name
        self.base_perms = base_perms
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.base_name),
            Label(f"Permission: {self.base_perms}"),
            Label(f"Id: {self.base_id}"),
            id="base-section",
        )
