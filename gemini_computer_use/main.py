"""Entry point for CLI execution."""
import argparse
import sys

from agent.config import GEMINI_API_KEY, MODEL_NAME, INITIAL_URL, SCREEN_WIDTH, SCREEN_HEIGHT, MAX_AGENT_TURNS
from agent.browser import BrowserManager
from agent.gemini_client import GeminiComputerUseClient
from agent.core import ComputerUseAgent
from agent.logger import get_logger

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run the Gemini Computer Use Agent.")
    parser.add_argument("goal", type=str, help="The goal description for the agent.")
    args = parser.parse_args()

    if not args.goal:
        logger.error("Goal argument missing.")
        sys.exit(1)

    try:
        browser = BrowserManager(page_width=SCREEN_WIDTH,
                                 page_height=SCREEN_HEIGHT,
                                 headless=False)

        llm = GeminiComputerUseClient(api_key=GEMINI_API_KEY,
                                      model_name=MODEL_NAME)

        agent = ComputerUseAgent(llm_client=llm,
                                 browser_manager=browser,
                                 max_turns=MAX_AGENT_TURNS)

        # TODO: Make agent async
        agent.run(goal=args.goal, initial_url=INITIAL_URL)

    except Exception as e:
        logger.error(f"Agent terminated due to exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
