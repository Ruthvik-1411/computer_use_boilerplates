"""Entry point for CLI execution."""
import argparse
import sys
import asyncio

from agent.config import (GEMINI_API_KEY, USE_VERTEXAI, VERTEXAI_PROJECT_ID, VERTEXAI_LOCATION,
                          MODEL_NAME, INITIAL_URL, SCREEN_WIDTH, SCREEN_HEIGHT, MAX_AGENT_TURNS)
from agent.browser import BrowserManager, AsyncBrowserManager
from agent.gemini_client import GeminiComputerUseClient
from agent.core import ComputerUseAgent, AsyncComputerUseAgent
from agent.logger import get_logger

logger = get_logger(__name__)

def run_agent_sync():
    """Runs the computer agent using CLI synchronously"""
    parser = argparse.ArgumentParser(description="Run the Gemini Computer Use Agent.")
    parser.add_argument("--goal", type=str, help="The goal description for the agent.")
    parser.add_argument("--initial_url", type=str, default=None, help="Initial URL to open (optional)")
    args = parser.parse_args()

    if not args.goal:
        logger.error("Goal argument missing.")
        sys.exit(1)

    try:
        browser = BrowserManager(page_width=SCREEN_WIDTH,
                                 page_height=SCREEN_HEIGHT,
                                 headless=False)

        if not USE_VERTEXAI:
            llm = GeminiComputerUseClient(api_key=GEMINI_API_KEY,
                                          model_name=MODEL_NAME)
        else:
            llm = GeminiComputerUseClient(vertexai_project=VERTEXAI_PROJECT_ID,
                                          vertexai_location=VERTEXAI_LOCATION)

        agent = ComputerUseAgent(llm_client=llm,
                                 browser_manager=browser,
                                 max_turns=MAX_AGENT_TURNS)

        agent.run(goal=args.goal, initial_url=args.initial_url or INITIAL_URL)

    except Exception as e:
        logger.error(f"Agent terminated due to exception: {e}", exc_info=True)
        sys.exit(1)

async def run_agent_async():
    """Runs the computer agent using CLI asynchronously"""
    parser = argparse.ArgumentParser(description="Run the Gemini Computer Use Agent.")
    parser.add_argument("--goal", type=str, help="The goal description for the agent.")
    parser.add_argument("--initial_url", type=str, default=None, help="Initial URL to open (optional)")
    args = parser.parse_args()

    if not args.goal:
        logger.error("Goal argument missing.")
        sys.exit(1)

    try:
        browser = AsyncBrowserManager(page_width=SCREEN_WIDTH,
                                     page_height=SCREEN_HEIGHT,
                                     headless=False)

        if not USE_VERTEXAI:
            llm = GeminiComputerUseClient(api_key=GEMINI_API_KEY,
                                          model_name=MODEL_NAME)
        else:
            llm = GeminiComputerUseClient(vertexai_project=VERTEXAI_PROJECT_ID,
                                          vertexai_location=VERTEXAI_LOCATION)

        agent = AsyncComputerUseAgent(llm_client=llm,
                                 browser_manager=browser,
                                 max_turns=MAX_AGENT_TURNS)

        await agent.run(goal=args.goal, initial_url=args.initial_url or INITIAL_URL)

    except Exception as e:
        logger.error(f"Agent terminated due to exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Run synchronously
    run_agent_sync()

    # Run asynchronously
    # asyncio.run(run_agent_async())
