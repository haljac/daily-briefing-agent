# Daily Briefing Agent
Daily Briefing Agent is a simple agentic tool that utilizes Google Gemini to generate a daily briefing. The tool is extensible so that you can register additional plugins that augment your briefing in whatever way you like.

# Getting Started
This application runs in a container by default. Use the compose file to run it.

> You must have the `GEMINI_API_KEY` environment variable set. You may place it in your `.env` file. See https://ai.google.dev/gemini-api/docs/api-key?hl=en

```
podman-compose up
```
