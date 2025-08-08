"""Main entry point for aidb-ai package."""

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel


def create_daily_briefing_agent():
    """Create the daily briefing AI agent."""
    model = GeminiModel('gemini-2.0-flash-exp')
    
    agent = Agent(
        model,
        system_prompt="You are a helpful AI assistant that provides daily briefings with weather and news.",
    )
    
    return agent


def main():
    """Main function for the aidb-ai package."""
    print("AI Daily Briefing - Core AI Models and Services")
    agent = create_daily_briefing_agent()
    print(f"Agent created with model: {agent.model}")


if __name__ == "__main__":
    main()