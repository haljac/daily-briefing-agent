"""Main CLI application for AI Daily Briefing using Typer and Rich."""

import asyncio
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from aidb_ai.main import AIDBAgent

# Initialize Rich console with color support
console = Console()

# Initialize Typer app
app = typer.Typer(
    name="aidb",
    help="🤖 AI Daily Briefing - Your intelligent daily companion",
    rich_markup_mode="rich",
)


class Session:
    """Manages the interactive chat session."""

    def __init__(self):
        self.agent = AIDBAgent()
        self.session_start = datetime.now()

    async def get_daily_briefing(self) -> str:
        """Get the initial daily briefing."""
        briefing_prompt = """
        Please provide my daily briefing including:
        1. Current weather information for my location
        2. Top news headlines with brief summaries
        
        Keep it concise but informative.
        """
        return await self.agent.request_async(briefing_prompt)

    async def chat_response(self, message: str) -> str:
        """Get a response from the AI agent."""
        return await self.agent.request_async(message)


def display_welcome():
    """Display the welcome message."""
    welcome_text = Text()
    welcome_text.append("🌅 ", style="yellow")
    welcome_text.append("AI Daily Briefing", style="bold blue")
    welcome_text.append(" 🤖", style="green")

    panel = Panel(
        welcome_text,
        subtitle="Your intelligent daily companion",
        border_style="bright_blue",
        padding=(1, 2)
    )
    console.print(panel)


def display_daily_briefing(briefing: str):
    """Display the daily briefing in a styled panel."""
    panel = Panel(
        briefing,
        title="📊 Daily Briefing",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)


def display_chat_message(message: str, is_user: bool = True):
    """Display a chat message with appropriate styling."""
    if is_user:
        prefix = "👤 You"
        style = "cyan"
        border_style = "cyan"
    else:
        prefix = "🤖 AI"
        style = "green"
        border_style = "green"

    panel = Panel(
        message,
        title=f"[{style}]{prefix}[/{style}]",
        border_style=border_style,
        padding=(0, 1)
    )
    console.print(panel)


async def interactive_chat_loop(session: Session):
    """Run the interactive chat loop."""
    console.print("\n💬 [bold yellow]Chat Mode[/bold yellow] - Type your questions or 'quit' to exit\n")

    while True:
        try:
            # Get user input with a styled prompt
            user_input = Prompt.ask("[cyan]You[/cyan]", console=console)

            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]👋 Goodbye! Have a great day![/yellow]")
                break

            if not user_input.strip():
                continue

            # Display user message
            display_chat_message(user_input, is_user=True)

            # Show thinking spinner while getting response
            with console.status("[bold green]🤖 AI is thinking...", spinner="dots"):
                response = await session.chat_response(user_input)

            # Display AI response
            display_chat_message(response, is_user=False)

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye! Have a great day![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")


@app.command()
def chat(
    skip_briefing: bool = typer.Option(
        False,
        "--skip-briefing",
        "-s",
        help="Skip the daily briefing and go straight to chat"
    )
):
    """Start an interactive chat session with the AI Daily Briefing bot."""

    # Display welcome message
    display_welcome()

    # Initialize chat session
    session = Session()

    async def run_session():
        if not skip_briefing:
            # Show daily briefing
            console.print("\n[bold yellow]📊 Getting your daily briefing...[/bold yellow]")

            with console.status("[bold blue]Fetching weather and news...", spinner="earth"):
                briefing = await session.get_daily_briefing()

            display_daily_briefing(briefing)

        # Start interactive chat
        await interactive_chat_loop(session)

    # Run the async session
    asyncio.run(run_session())


@app.command()
def briefing():
    """Get just the daily briefing without entering chat mode."""

    display_welcome()

    session = Session()

    async def get_briefing():
        console.print("\n[bold yellow]📊 Getting your daily briefing...[/bold yellow]")

        with console.status("[bold blue]Fetching weather and news...", spinner="earth"):
            briefing = await session.get_daily_briefing()

        display_daily_briefing(briefing)

    asyncio.run(get_briefing())


def main():
    """Main entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()

