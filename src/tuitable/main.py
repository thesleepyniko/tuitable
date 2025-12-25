from textual.app import App, ComposeResult
from dotenv import load_dotenv
from .components import WelcomeScreen, AuthenticationChoiceScreen

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Label, Button
from textual.containers import CenterMiddle

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
        await self.push_screen(WelcomeScreen(), self.on_welcome_complete) # type: ignore

    def on_welcome_complete(self, result) -> None: # type: ignore
        """Called when WelcomeScreen is dismissed"""
        self.push_screen(AuthenticationChoiceScreen(), self.on_auth_complete) # type: ignore
    
    def on_auth_complete(self, result) -> None: # type: ignore
        """Called when AuthenticationChoiceScreen is dismissed"""
        # Push next screen or start main app
        pass

def main():
    load_dotenv()
    app = TuiTable()
    app.run()


if __name__ == "__main__":
    main()
