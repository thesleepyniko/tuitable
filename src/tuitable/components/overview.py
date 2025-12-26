import asyncio
import base64
import hashlib
import secrets
import webbrowser

import httpx
from aiohttp import web
from requests import Request
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Middle, VerticalScroll, CenterMiddle
from textual.message import Message
from textual.events import Click
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Label

from ..util.credentials import get_token

TITLE = r""" 
 _____      _ _____     _     _      
|_   _|   _(_)_   _|_ _| |__ | | ___ 
  | || | | | | | |/ _` | '_ \| |/ _ \
  | || |_| | | | | (_| | |_) | |  __/
  |_| \__,_|_| |_|\__,_|_.__/|_|\___|"""

class OverviewScreen(Screen[str]):
    CSS_PATH = "overview.tcss"

    def __init__(self, token: str):
        self.token = token
        self.bases = []
        super().__init__()

    async def on_mount(self):
        container = self.query_one("#bases-container", VerticalScroll)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.airtable.com/v0/meta/bases",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                self.notify(str(response.status_code))
                self.notify("TuiTable could not contact Airtable. Relaunch the app in a few seconds.")
                return
            
            response_data = response.json()
            self.notify(str(response_data))
            self.bases = response_data.get("bases", [])
            self.notify(str(self.bases))
            
            for base in self.bases:
                await container.mount(BaseWidget(base["id"], base["name"], base["permissionLevel"]))

    def compose(self) -> ComposeResult: 
        yield Vertical(
            Label(TITLE),
            VerticalScroll(id="bases-container")  
        )


class BaseWidget(Widget):

    def __init__(self, base_id: str, base_name: str, base_perms: str) -> None:
        self.base_id = base_id
        self.base_name = base_name
        self.base_perms = base_perms
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Vertical(
            CenterMiddle(
                Label(self.base_name),
                Label(f"Permission: {self.base_perms}"),
                Label(f"Id: {self.base_id}")
                ),
            id="base-section",
        )
    
    def on_click(self, message: Message) -> None:
        """An event handler called when the widget is clicked."""
        self.notify("hi!")
        message.stop() 
