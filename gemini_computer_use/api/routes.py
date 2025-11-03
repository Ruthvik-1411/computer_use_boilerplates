"""API routes for Gemini Computer Use Agent"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic.config import ConfigDict

from agent.config import GEMINI_API_KEY,MODEL_NAME, SCREEN_WIDTH, SCREEN_HEIGHT, MAX_AGENT_TURNS
from agent.browser import BrowserManager, AsyncBrowserManager
from agent.gemini_client import GeminiComputerUseClient
from agent.core import ComputerUseAgent, AsyncComputerUseAgent
from agent.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Gemini Agent"])

class AgentRunRequest(BaseModel):
    """Request data model for Agent Run Request"""
    goal: str
    url: Optional[str] = ""
    max_turns: Optional[int] = MAX_AGENT_TURNS

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "goal": "What is today's featured article on wikipedia about?",
            "url": "https://en.wikipedia.org/wiki/Main_Page",
            "max_turns": 10
        }]
    })

class AgentRunResponse(BaseModel):
    """Response data model for Agent Run Response"""
    success: bool
    message: str

@router.post("/run_agent_sync", response_model=AgentRunResponse)
def run_agent_sync(req: AgentRunRequest):
    """Runs the Gemini Computer Use Agent with the given goal"""

    try:
        browser = BrowserManager(
            page_width=SCREEN_WIDTH,
            page_height=SCREEN_HEIGHT,
            # Read this based on env, for containers, read the respective variable
            headless=True,
        )

        llm = GeminiComputerUseClient(
            api_key=GEMINI_API_KEY,
            model_name=MODEL_NAME,
        )

        agent = ComputerUseAgent(
            llm_client=llm,
            browser_manager=browser,
            max_turns=req.max_turns,
        )

        # Run the agent synchronously for now
        # TODO: Propagate errors/exceptions to client, supressing for now inside .run
        result_text = agent.run(goal=req.goal, initial_url=req.url)

        return AgentRunResponse(success=True,
                                message=result_text or "Agent run completed successfully.")

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run_agent_async", response_model=AgentRunResponse)
async def run_agent_async(req: AgentRunRequest):
    """Runs the Gemini Computer Use Agent with the given goal asynchronously"""

    try:
        browser = AsyncBrowserManager(
            page_width=SCREEN_WIDTH,
            page_height=SCREEN_HEIGHT,
            # Read this based on env, for containers, read the respective variable
            headless=True,
        )

        llm = GeminiComputerUseClient(
            api_key=GEMINI_API_KEY,
            model_name=MODEL_NAME,
        )

        agent = AsyncComputerUseAgent(
            llm_client=llm,
            browser_manager=browser,
            max_turns=req.max_turns,
        )

        # TODO: Propagate errors/exceptions to client, supressing for now inside .run
        result_text = await agent.run(goal=req.goal, initial_url=req.url)

        return AgentRunResponse(success=True,
                                message=result_text or "Agent run completed successfully.")

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
