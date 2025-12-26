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
from textual.widgets import Button, Label

from ..util.credentials import save_token

TITLE = r""" 
 _____      _ _____     _     _      
|_   _|   _(_)_   _|_ _| |__ | | ___ 
  | || | | | | | |/ _` | '_ \| |/ _ \
  | || |_| | | | | (_| | |_) | |  __/
  |_| \__,_|_| |_|\__,_|_.__/|_|\___|"""

class LoadingScreen(Screen[None]):

    CSS_PATH = "onboarding.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    TITLE,
                    classes="title",
                ),
                Label(
                    "Loading user info..."
                ),
                Label(
                    "Made with <3 and :D by niko\nOpen Sourced at github.com/thesleepyniko/tuitable",
                    id="love-text",
                ),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )

class WelcomeScreen(Screen[bool]):
    """
    Screen intended to be launched once upon intialization
    """

    CSS_PATH = "onboarding.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    TITLE,
                    classes="title",
                ),
                Label(
                    "An Airtable client for your terminal.\nSelecting continue will open a browser window for authentication."
                ),
                Button("Continue", id="continue"),
                Label(
                    "Made with <3 and :D by niko\nOpen Sourced at github.com/thesleepyniko/tuitable",
                    id="love-text",
                ),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "continue":
            self.dismiss(False)
            event.stop()


# class AuthenticationChoiceScreen(Screen[str]):

#     CSS_PATH = "onboarding.tcss"

#     def compose(self) -> ComposeResult:
#         yield Horizontal(
#             Middle(
#                 Label(
#                     TITLE,
#                     classes="title",
#                 ),
#                 Label("Select continue to open a browser window for authentication."),
#                 Button("Continue"),
#                 id="welcome",
#             ),
#             Container(id="hatch-red"),
#             Container(id="hatch-yellow"),
#             Container(id="hatch-blue"),
#         )

#     def on_button_pressed(self, event: Button.Pressed):
#         self.dismiss()
#         event.stop()


class AuthenticationInputScreen(Screen[bool]):
    CSS_PATH = "onboarding.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    TITLE,
                    classes="title",
                ),
                Label(
                    "A browser tab should've been opened. Once you are finished authenticating, return to TuiTable."
                ),
                Button("Back", id="back"),
                Label(
                    "Made with <3 and :D by niko\nOpen Sourced at github.com/thesleepyniko/tuitable",
                    id="love-text",
                ),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )

    async def handle_callback(self, request: web.Request) -> web.Response:
        self.code = request.rel_url.query.get("code")
        return_state = request.rel_url.query.get("state")
        return_challenge = request.rel_url.query.get("code_challenge")
        error = request.rel_url.query.get("error")

        if error:
            # TODO: add logging to a file
            self.notify(
                "There was an error with the authorization. Try again in a few seconds."
            )
            self.dismiss(False)
            return web.Response(text="Authorization failed", status=400)

        if return_state != self.state or return_challenge != self.code_challenge:
            self.notify(
                "TuiTable detected a security error. Try again in a few seconds."
            )
            self.dismiss(False)
            return web.Response(text="Security validation failed", status=400)

        else:
            response = httpx.post(
                "https://airtable.com/oauth2/v1/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "code": self.code,
                    "client_id": self.client_id,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                    "code_verifier": self.code_verifier,
                },
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                self.notify(
                    "TuiTable encountered an error contacting Airtable. Try again in a few seconds."
                )
                self.dismiss(False)
                return web.Response(text="Token exchange failed", status=400)
            response = response.json()
            save_token(response.get("access_token"), "access")
            save_token(response.get("refresh_token"), "refresh")
            self.dismiss(True)
            return web.Response(text="Authorization successful", status=200)

    async def start_server(self):
        app = web.Application()
        app.router.add_get("/callback", self.handle_callback)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8000)
        await site.start()

    async def on_mount(self):
        self.state = secrets.token_hex(16)
        self.redirect_uri = "http://localhost:8000/callback"
        self.response_type = "code"
        self.scope = "data.records:read data.records:write data.recordComments:write data.recordComments:read schema.bases:read schema.bases:write user.email:read"
        self.client_id = "baf81178-c674-4cdf-ab29-bd9c4e4fbeff"
        self.code_verifier = (
            base64.urlsafe_b64encode(secrets.token_bytes(32))
            .decode("utf-8")
            .rstrip("=")
        )
        challenge_bytes = hashlib.sha256(self.code_verifier.encode("ascii")).digest()
        self.code_challenge = (
            base64.urlsafe_b64encode(challenge_bytes).decode("utf-8").rstrip("=")
        )

        self.params = {
            "state": self.state,
            "redirect_uri": self.redirect_uri,
            "response_type": self.response_type,
            "scope": self.scope,
            "client_id": self.client_id,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }

        req = Request(
            "GET", "https://airtable.com/oauth2/v1/authorize", params=self.params
        )

        webbrowser.open_new_tab(req.prepare().url)  # type: ignore

        await self.start_server()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.dismiss(False)
            event.stop()
        else:
            self.dismiss(True)
            event.stop()


class FinishOnboarding(Screen[None]):

    CSS_PATH="onboarding.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    TITLE,
                    classes="title",
                ),
                Label("You're authenticated!\nWelcome to TuiTable. Let's get started."),
                Button("Get Started", id="get-started", disabled=True),
                Label(
                    "Made with <3 and :D by niko\nOpen Sourced at github.com/thesleepyniko/tuitable",
                    id="love-text",
                ),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()
        event.stop()
