"""Central configuration settings."""
import os
from dotenv import load_dotenv

load_dotenv()

USE_VERTEXAI = os.getenv("USE_VERTEXAI", "false").lower() == "true"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VERTEXAI_PROJECT_ID = os.getenv("VERTEXAI_PROJECT_ID")
VERTEXAI_LOCATION = os.getenv("VERTEXAI_LOCATION")

MODEL_NAME = "gemini-2.5-computer-use-preview-10-2025"

if not GEMINI_API_KEY and not USE_VERTEXAI:
    raise ValueError("Please set either GEMINI_API_KEY or USE_VERTEXAI=true in .env")

if USE_VERTEXAI and (not VERTEXAI_PROJECT_ID or not VERTEXAI_LOCATION):
    raise ValueError("Please set VERTEXAI_PROJECT_ID and VERTEXAI_LOCATION in .env")

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900

# Default value, expects url from CLI else starts with search engine
INITIAL_URL = None

# Fill a google form
# INITIAL_URL = "https://forms.gle/HnVvLVSseEvuPaaAA"

# Try to solve a captcha
# INITIAL_URL = "https://2captcha.com/demo/recaptcha-v2"

MAX_AGENT_TURNS = 20