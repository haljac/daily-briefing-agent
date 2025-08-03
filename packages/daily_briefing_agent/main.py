import os
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable not set.")

def main():
    print("Hello from daily-briefing-agent!")


if __name__ == "__main__":
    main()
