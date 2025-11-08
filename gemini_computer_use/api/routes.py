"""API routes for Gemini Computer Use Agent"""
from typing import Optional, List, Dict, Any, Literal

import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic.config import ConfigDict

from agent.config import (GEMINI_API_KEY, USE_VERTEXAI, VERTEXAI_PROJECT_ID, VERTEXAI_LOCATION,
                          MODEL_NAME, SCREEN_WIDTH, SCREEN_HEIGHT, MAX_AGENT_TURNS)
from agent.browser import AsyncBrowserManager
from agent.gemini_client import GeminiComputerUseClient
from agent.core import AsyncComputerUseAgent
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
    termination_reason: Literal["COMPLETED", "MAX_TURNS_EXCEEDED", "ERROR"] = "ERROR"
    message: str
    action_history: List[Dict[str, Any]]
    final_screenshot: Optional[str] = None

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

        if not USE_VERTEXAI:
            llm = GeminiComputerUseClient(api_key=GEMINI_API_KEY,
                                          model_name=MODEL_NAME)
        else:
            llm = GeminiComputerUseClient(vertexai_project=VERTEXAI_PROJECT_ID,
                                          vertexai_location=VERTEXAI_LOCATION,
                                          model_name=MODEL_NAME)

        agent = AsyncComputerUseAgent(
            llm_client=llm,
            browser_manager=browser,
            max_turns=req.max_turns,
        )

        result_dict = await agent.run(goal=req.goal, initial_url=req.url)

        screenshot_b64 = None

        if result_dict.get("final_screenshot_bytes"):
            screenshot_b64 = base64.b64encode(result_dict["final_screenshot_bytes"]).decode('utf-8')

        is_success = result_dict["termination_reason"] == "COMPLETED"

        return AgentRunResponse(
            success=is_success,
            termination_reason=result_dict["termination_reason"],
            message=result_dict["final_message"],
            action_history=result_dict["action_history"],
            final_screenshot=screenshot_b64,
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
