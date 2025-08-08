from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

load_dotenv()


class AIDBAgent:
    def __init__(self):
        self.agent = create_daily_briefing_agent()
        self.message_history = []

    def request(self, query: str):
        """Query the AI agent for a daily briefing."""
        return self.agent.run_sync(user_prompt=query)

    async def request_async(self, query: str):
        """Query the AI agent asynchronously."""
        result = await self.agent.run(user_prompt=query, message_history=self.message_history)
        self.message_history.extend(result.new_messages())
        return result.output


def create_daily_briefing_agent():
    """Create the daily briefing AI agent."""
    model = GoogleModel(model_name="gemini-2.5-flash")

    return Agent(
        model,
        system_prompt="""
You are a helpful AI assistant that provides daily briefings with weather and news.
        """,
    )
