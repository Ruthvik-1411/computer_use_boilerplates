"""Central configuration settings."""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Please make sure `GEMINI_API_KEY` is added to .env")

MODEL_NAME = "gemini-2.5-computer-use-preview-10-2025"

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900

# Fill a google form
INITIAL_URL = "https://forms.gle/HnVvLVSseEvuPaaAA"

# Try to solve a captcha
# INITIAL_URL = "https://2captcha.com/demo/recaptcha-v2"

MAX_AGENT_TURNS = 20