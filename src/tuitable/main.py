import httpx
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import CenterMiddle
from textual.screen import Screen
from textual.widgets import Button, Label

from .components import AuthenticationInputScreen, FinishOnboarding, WelcomeScreen, LoadingScreen
from .util.credentials import get_token, save_token

# class WelcomeScreen(Screen):
#     """
#     Screen intended to be launched once upon intialization
#     """

#     def compose(self) -> ComposeResult:
#         yield Center(
#             Label("Welcome to TuiTable"),
#             Label("Airtable right in your terminal."),
#             Button("Continue")
#         )


class TuiTable(App):
    async def on_mount(self) -> None:
        self.push_screen(LoadingScreen())
        client_id = "baf81178-c674-4cdf-ab29-bd9c4e4fbeff"
        refresh_token = get_token(token_type="refresh")
        if refresh_token and isinstance(refresh_token, str):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://airtable.com/oauth2/v1/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": client_id,
                    },
                )
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError:
                    self.notify(
                        "TuiTable encountered an error contacting Airtable. Try again in a few seconds."
                    )
                response_data = response.json()
                save_token(response_data.get("access_token"), "access")
                save_token(response_data.get("refresh_token"), "refresh")
            self.pop_screen()
            await self.push_screen(FinishOnboarding(), self.on_welcome_complete)  # type: ignore
            return
        self.pop_screen()
        self.push_screen(WelcomeScreen(), self.on_welcome_complete)
        

    def on_welcome_complete(self, result: bool | None) -> None:  # type: ignore
        """Called when WelcomeScreen is dismissed"""
        if result:
            self.push_screen(FinishOnboarding(), self.on_start_tutorial)  # type: ignore
        else:
            self.push_screen(AuthenticationInputScreen(), self.on_auth_entry_complete)

    def on_auth_entry_complete(self, result: bool | None) -> None:
        if result is False:
            self.push_screen(WelcomeScreen(), self.on_welcome_complete)
        else:
            self.push_screen(FinishOnboarding(), self.on_start_tutorial)

    def on_start_tutorial(self, result: None) -> None:
        pass


def main():
    load_dotenv()
    app = TuiTable()
    app.run()


if __name__ == "__main__":
    main()
