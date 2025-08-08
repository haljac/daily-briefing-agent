"""Main entry point for aidb-tui package."""

from textual.app import App
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical

from aidb_ai.main import create_daily_briefing_agent


class DailyBriefingApp(App):
    """TUI application for the daily briefing bot."""
    
    CSS = """
    Static {
        padding: 1;
        margin: 1;
        border: solid $primary;
    }
    """

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        with Vertical():
            yield Static("Welcome to AI Daily Briefing!", id="welcome")
            yield Static("Loading daily briefing...", id="briefing")
        yield Footer()

    async def on_mount(self):
        """Called when app starts."""
        agent = create_daily_briefing_agent()
        briefing_widget = self.query_one("#briefing", Static)
        briefing_widget.update("Daily briefing agent initialized!")


def main():
    """Main function for the aidb-tui package."""
    app = DailyBriefingApp()
    app.run()


if __name__ == "__main__":
    main()