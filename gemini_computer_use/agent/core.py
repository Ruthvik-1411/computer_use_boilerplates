"""Main agent orchestration logic"""
from typing import Optional, List, Dict, Any

from .gemini_client import GeminiComputerUseClient
from .browser import BrowserManager, AsyncBrowserManager
from .utils import get_safety_confirmation, time_logger
from .logger import get_logger

logger = get_logger(__name__)

class ComputerUseAgent:
    """Class for orchestrating the computer use agent"""

    def __init__(self,
                 llm_client: GeminiComputerUseClient,
                 browser_manager: BrowserManager,
                 max_turns: int = 20):
        self.llm = llm_client
        self.browser = browser_manager
        self.max_turns = max_turns

    def _execute_function_calls(self, function_calls):
        """Executes the function calls using browser actions"""
        results = []
        for fc in function_calls:
            fc_name = fc.name
            fc_args = dict(fc.args or {})
            action_result = {}

            if "safety_decision" in fc_args:
                decision = get_safety_confirmation(fc_args["safety_decision"])
                if decision == "TERMINATE":
                    logger.warning("Terminating agent loop due to safety request.")
                    break
                action_result["safety_acknowledgement"] = "true"
        
            result = self.browser.execute_action(fc_name, fc_args)
            action_result.update(result)
            results.append((fc_name, action_result))
        return results

    @time_logger
    def run(self, goal: str, initial_url: Optional[str] = None):
        """Runs the main agent loop"""
        final_response = ""
        termination_reason = "ERROR"
        action_history: List[Dict[str, Any]] = []
        final_screenshot: bytes = b""

        try:
            self.browser.start()
            if initial_url:
                logger.info(f"Starting browser with url: {initial_url}")
                self.browser.goto(initial_url)
            else:
                logger.info("No initial URL provided. Opening default search engine.")
                self.browser.search()

            logger.info(f"Agent goal: {goal}")

            # Capture initial state
            initial_image = self.browser.capture_screen()
            contents = self.llm.build_initial_message(goal, initial_image)

            # Run the react loop for max_turns
            for turn in range(self.max_turns):
                logger.info(f"===== Turn {turn + 1}/{self.max_turns} =====")
                
                # Generate content
                response = self.llm.generate_content(contents)
                # logger.info(f"[RESPONSE] {response.model_dump()}")
                candidate = response.candidates[0]
                contents.append(candidate.content)

                function_calls = [
                    p.function_call
                    for p in candidate.content.parts
                    if getattr(p, "function_call", None)
                ]

                # If no function calls, then task complete
                if not function_calls:
                    final_response = " ".join(
                        [p.text for p in candidate.content.parts if p.text]
                    )
                    logger.info(f"[Final Output]: {final_response}")
                    termination_reason = "COMPLETED"
                    break
                
                # Execute actions and send back screenshots
                action_results = self._execute_function_calls(function_calls)

                for i, fc in enumerate(function_calls):
                    action_history.append({
                        "turn": turn + 1,
                        "action_name": fc.name,
                        "action_args": dict(fc.args or {}),
                        "result": action_results[i][1]
                    })

                screenshot = self.browser.capture_screen()
                current_url = self.browser.get_current_url()

                function_response_content = self.llm.build_function_responses_message(
                    screenshot=screenshot,
                    current_url=current_url,
                    results=action_results
                )

                # Update state with function responses
                contents.append(function_response_content)
            else:
                # Reached max_turns without reaching a final output
                logger.warning("Exhausted maximum number of turns. Unable to achieve goal.")
                final_response = "Goal not completed within the maximum turn limit."
                termination_reason = "MAX_TURNS_EXCEEDED"

        except Exception as e:
            logger.error(f"Agent encountered an error: {e}", exc_info=True)
            final_response = f"Agent terminated due to error: {e}"
            termination_reason = "ERROR"
        finally:
            if self.browser and self.browser.page:
                final_screenshot = self.browser.capture_screen()

            self.browser.close()
        
        return {
            "final_message": final_response,
            "action_history": action_history,
            "termination_reason": termination_reason,
            "final_screenshot_bytes": final_screenshot
        }

class AsyncComputerUseAgent:
    """Class for orchestrating the computer use agent asynchronously"""

    def __init__(self,
                 llm_client: GeminiComputerUseClient,
                 browser_manager: AsyncBrowserManager,
                 max_turns: int = 20):
        self.llm = llm_client
        self.browser = browser_manager
        self.max_turns = max_turns

    async def _execute_function_calls(self, function_calls):
        """Executes the function calls using browser actions"""
        results = []
        for fc in function_calls:
            fc_name = fc.name
            fc_args = dict(fc.args or {})
            action_result = {}

            if "safety_decision" in fc_args:
                decision = get_safety_confirmation(fc_args["safety_decision"])
                if decision == "TERMINATE":
                    logger.warning("Terminating agent loop due to safety request.")
                    break
                action_result["safety_acknowledgement"] = "true"
        
            result = await self.browser.execute_action(fc_name, fc_args)
            action_result.update(result)
            results.append((fc_name, action_result))
        return results

    @time_logger
    async def run(self, goal: str, initial_url: Optional[str] = None):
        """Runs the main agent loop"""
        final_response = ""
        termination_reason = "ERROR"
        action_history: List[Dict[str, Any]] = []
        final_screenshot: bytes = b""

        try:
            await self.browser.start()
            if initial_url:
                logger.info(f"Starting browser with url: {initial_url}")
                await self.browser.goto(initial_url)
            else:
                logger.info("No initial URL provided. Opening default search engine.")
                await self.browser.search()

            logger.info(f"Agent goal: {goal}")

            # Capture initial state
            initial_image = await self.browser.capture_screen()
            contents = self.llm.build_initial_message(goal, initial_image)

            # Run the react loop for max_turns
            for turn in range(self.max_turns):
                logger.info(f"===== Turn {turn + 1}/{self.max_turns} =====")
                
                # Generate content
                response = await self.llm.generate_content_async(contents)
                # logger.info(f"[RESPONSE] {response.model_dump()}")
                candidate = response.candidates[0]
                contents.append(candidate.content)

                function_calls = [
                    p.function_call
                    for p in candidate.content.parts
                    if getattr(p, "function_call", None)
                ]

                # If no function calls, then task complete
                if not function_calls:
                    final_response = " ".join(
                        [p.text for p in candidate.content.parts if p.text]
                    )
                    logger.info(f"[Final Output]: {final_response}")
                    termination_reason = "COMPLETED"
                    break
                
                # Execute actions and send back screenshots
                action_results = await self._execute_function_calls(function_calls)

                for i, fc in enumerate(function_calls):
                    action_history.append({
                        "turn": turn + 1,
                        "action_name": fc.name,
                        "action_args": dict(fc.args or {}),
                        "result": action_results[i][1]
                    })

                screenshot = await self.browser.capture_screen()
                current_url = await self.browser.get_current_url()

                function_response_content = self.llm.build_function_responses_message(
                    screenshot=screenshot,
                    current_url=current_url,
                    results=action_results
                )

                # Update state with function responses
                contents.append(function_response_content)
            else:
                # Reached max_turns without reaching a final output
                logger.warning("Exhausted maximum number of turns. Unable to achieve goal.")
                final_response = "Goal not completed within the maximum turn limit."
                termination_reason = "MAX_TURNS_EXCEEDED"

        except Exception as e:
            logger.error(f"Agent encountered an error: {e}", exc_info=True)
            final_response = f"Agent terminated due to error: {e}"
            termination_reason = "ERROR"
        finally:
            if self.browser and self.browser.page:
                final_screenshot = await self.browser.capture_screen()

            await self.browser.close()
        
        return {
            "final_message": final_response,
            "action_history": action_history,
            "termination_reason": termination_reason,
            "final_screenshot_bytes": final_screenshot
        }
