import asyncio
import base64
import hashlib
import secrets
import webbrowser
from requests import Request, Session

from aiohttp import web
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Middle
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from ..util.credentials import save_token

TITLE = r""" 
 _____      _ _____     _     _      
|_   _|   _(_)_   _|_ _| |__ | | ___ 
  | || | | | | | |/ _` | '_ \| |/ _ \
  | || |_| | | | | (_| | |_) | |  __/
  |_| \__,_|_| |_|\__,_|_.__/|_|\___|"""

class WelcomeScreen(Screen[None]):
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
                Label("An Airtable client for your terminal."),
                Button("Continue", id="continue"),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "continue":
            self.dismiss()
            event.stop()

class AuthenticationChoiceScreen(Screen[str]):

    CSS_PATH = "onboarding.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    TITLE,
                    classes="title",
                ),
                Label("Select continue to open a browser window for authentication."),
                Button("Continue"),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()
        event.stop()

class AuthenticationInputScreen(Screen[bool]):

    CSS_PATH = "onboarding.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    TITLE,
                    classes="title",
                ),
                Label("A browser tab should've been opened. Once you are finished authenticating, return to TuiTable."),
                Button("Continue", id="continue", disabled=True),
                Button("Back", id="back"),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )

    def handle_callback(self, request: web.Request):
        token = request.rel_url.query.get("code")
        return_state = request.rel_url.query.get("state")
        return_challenge = request.rel_url.query.get("code_challenge")
        error = request.rel_url.query.get("error")

        if error:
            #TODO: add logging to a file
            self.notify("There was an error with the authorization. Try again in a few seconds.")
            return

        if return_state != self.state or return_challenge != self.code_challenge:
            self.notify("TuiTable detected a security error. Try again in a few seconds.")
            return
            
    
    # def start_server(self):
        # app = web.Application()
        # app.router.add_get('/callback')

    async def on_mount(self):
        self.state = secrets.token_hex(16)
        self.redirect_uri = "http://localhost:8000/callback"
        self.response_type = "code"
        self.scope = "data.records:read data.records:write data.recordComments:write data.recordComments:read schema.bases:read schema.bases:write user.email:read"
        self.client_id = "baf81178-c674-4cdf-ab29-bd9c4e4fbeff"
        self.code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        challenge_bytes = hashlib.sha256(self.code_verifier.encode('ascii')).digest()
        self.code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

        self.params = {
            "state": self.state, 
            "redirect_uri": self.redirect_uri,
            "response_type": self.response_type,
            "scope": self.scope,
            "client_id": self.client_id,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256"
        }

        req = Request('GET', "https://airtable.com/oauth2/v1/authorize", params=self.params)

        webbrowser.open_new_tab(req.prepare().url)




    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.dismiss(False)
            event.stop()
        else:
            self.dismiss(True)
            event.stop()
       
        