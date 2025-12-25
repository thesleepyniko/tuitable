from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Label, Button
from textual.containers import Middle, Horizontal, Container

class WelcomeScreen(Screen):
    """
    Screen intended to be launched once upon intialization
    """

    CSS_PATH = "onboarding.tcss"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    r""" 
 _____      _ _____     _     _      
|_   _|   _(_)_   _|_ _| |__ | | ___ 
  | || | | | | | |/ _` | '_ \| |/ _ \
  | || |_| | | | | (_| | |_) | |  __/
  |_| \__,_|_| |_|\__,_|_.__/|_|\___|""",
                    classes="title",
                ),
                Label("Airtable right in your terminal. All local, all open source."),
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

class AuthenticationChoiceScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Middle(
                Label(
                    r""" 
 _____      _ _____     _     _      
|_   _|   _(_)_   _|_ _| |__ | | ___ 
  | || | | | | | |/ _` | '_ \| |/ _ \
  | || |_| | | | | (_| | |_) | |  __/
  |_| \__,_|_| |_|\__,_|_.__/|_|\___|""",
                    classes="title",
                ),
                Label("Select a method to authenticate. All data will be stored locally."),
                Button("Personal Access Token (PAT)", id="pat"),
                Button("OAuth", id="oauth"),
                id="welcome",
            ),
            Container(id="hatch-red"),
            Container(id="hatch-yellow"),
            Container(id="hatch-blue"),
        )