import os
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel

from .config import ConfigManager

load_dotenv()


class AgentDeps:
    """Dependencies for the AI agent."""

    def __init__(
            self,
            news_api_key: str,
            weather_api_key: str,
            zip_code: str | None = None):
        self.news_api_key = news_api_key
        self.weather_api_key = weather_api_key
        self.zip_code = zip_code


class AIDBAgent:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.agent = create_daily_briefing_agent()
        self.message_history = []

    def request(self, query: str):
        """Query the AI agent for a daily briefing."""
        deps = self._create_deps()
        return self.agent.run_sync(user_prompt=query, deps=deps)

    async def request_async(self, query: str):
        """Query the AI agent asynchronously."""
        deps = self._create_deps()
        result = await self.agent.run(
            user_prompt=query, message_history=self.message_history, deps=deps
        )
        self.message_history.extend(result.new_messages())
        return result.output

    def _create_deps(self) -> AgentDeps:
        """Create dependencies for the agent."""
        news_api_key = os.getenv("NEWS_API_KEY", "")
        weather_api_key = os.getenv("WEATHER_API_KEY", "")
        zip_code = self.get_zip_code()
        return AgentDeps(
            news_api_key=news_api_key,
            weather_api_key=weather_api_key,
            zip_code=zip_code)

    def get_zip_code(self) -> str | None:
        """Get the configured zip code."""
        return self.config_manager.get_zip_code()

    def set_zip_code(self, zip_code: str) -> None:
        """Set the zip code in configuration."""
        self.config_manager.update_zip_code(zip_code)

    def needs_zip_code(self) -> bool:
        """Check if zip code configuration is needed."""
        return self.config_manager.needs_zip_code()

    async def get_daily_briefing(self) -> str:
        """Get the daily briefing with weather and news."""
        zip_code = self.get_zip_code()
        zip_info = f" for zip code {zip_code}" if zip_code else ""

        briefing_prompt = f"""
        Please provide my daily briefing including:
        1. Current weather information{zip_info}
        2. Top news headlines with brief summaries using the get_headlines tool

        Keep it concise but informative. Use the tools available to get real data.
        """
        return await self.request_async(briefing_prompt)


def create_daily_briefing_agent():
    """Create the daily briefing AI agent."""
    model = GoogleModel(model_name="gemini-2.5-flash")

    agent = Agent(
        model,
        deps_type=AgentDeps,
        system_prompt="""
You are a helpful AI assistant that provides daily briefings with weather and news.
When provided with a zip code, try to give location-specific weather information.
Use the get_headlines tool to fetch real news headlines when requested.
        """,
    )

    @agent.tool
    async def get_headlines(
        ctx: RunContext[AgentDeps], country: str = "us"
    ) -> list[dict[str, Any]]:
        """Fetch top news headlines from NewsAPI."""
        if not ctx.deps.news_api_key:
            return [
                {
                    "title": "News API key not configured",
                    "description": "Please set NEWS_API_KEY environment variable",
                }
            ]

        url = (
            f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={ctx.deps.news_api_key}"
        )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                articles = data.get("articles", [])[:5]  # Get top 5 headlines

                # Return simplified structure for the AI
                return [
                    {
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "published_at": article.get("publishedAt", ""),
                    }
                    for article in articles
                ]
            except httpx.RequestError as e:
                return [
                    {
                        "title": f"Error fetching news: {e}",
                        "description": "Could not retrieve news headlines",
                    }
                ]
            except Exception as e:
                return [
                    {
                        "title": f"Unexpected error: {e}",
                        "description": "An error occurred while fetching news",
                    }
                ]

    @agent.tool
    async def get_weather(
        ctx: RunContext[AgentDeps]
    ) -> list[dict[str, Any]]:
        """Fetch top news headlines from WeatherAPI."""
        if not ctx.deps.news_api_key:
            return [
                {
                    "title": "Weather API key not configured",
                    "description": "Please set WEATHER_API_KEY environment variable",
                }
            ]

        url = (
            f"http://api.weatherapi.com/v1/current.json?key={ctx.deps.weather_api_key}&q={ctx.deps.zip_code or 'auto:ip'}"
        )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                weather = data.get("current", {})
                location = data.get("location", {})
                city = location.get("name", ""),
                region = location.get("region", ""),
                country =location.get("country", ""),

                return [
                    {
                        "title": f"Current Weather for {city}, {region}, {country}",
                        "temp_f": weather.get("temp_f", ""),
                        "humidity": weather.get("humidity", ""),
                        "last_updated": weather.get("last_updated", ""),
                    }
                ]
            except httpx.RequestError as e:
                return [
                    {
                        "title": f"Error fetching weather: {e}",
                        "description": "Could not retrieve current weather",
                    }
                ]
            except Exception as e:
                return [
                    {
                        "title": f"Unexpected error: {e}",
                        "description": "An error occurred while fetching weather",
                    }
                ]

    return agent
