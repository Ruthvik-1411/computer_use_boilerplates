"""Encapsulate LLM (Gemini) interactions."""
from typing import List, Dict, Any, Optional
from google.genai import Client, types

from .utils import time_logger
from .logger import get_logger

logger = get_logger(__name__)

class GeminiComputerUseClient:
    """Gemini client class"""

    def __init__(self,
                 api_key: Optional[str] = None,
                 vertexai_project: Optional[str] = None,
                 vertexai_location: Optional[str] = None,
                 model_name: str = "gemini-2.5-computer-use-preview-10-2025",
                 system_instructions: str = ""):
        """Initializes a Gemini client instance.

        Args:
            api_key: Gemini API key to use google developer api endpoints.
            vertexai_project: GCP project ID for Vertex AI usage.
            vertexai_location: GCP region for Vertex AI usage.
            model_name: Gemini model name.
            system_instructions: Optional system instructions.
        """
        if api_key:
            logger.info("Using Gemini with API key.")
            self.gemini_client = Client(
                api_key=api_key
            )
        elif vertexai_project and vertexai_location:
            logger.info(
                f"Using Vertex AI endpoints for project: `{vertexai_project}` "
                f"in location: `{vertexai_location}`."
            )
            self.gemini_client = Client(
                vertexai=True,
                project=vertexai_project,
                location=vertexai_location
            )
        else:
            raise ValueError(
                "GeminiComputerUseClient requires either `api_key` "
                "or both `vertexai_project` and `vertexai_location`."
            )
        
        self.model_name = model_name
        self.system_instructions = system_instructions
        self.excluded_functions = [
            # "drag_and_drop",
            "open_web_browser"
        ]
        self._setup_config()

    def _setup_config(self):
        """Set up the generation config"""
        if self.system_instructions:
            system_instructions_contents = types.Content(
                role="system",
                parts=[types.Part(text=self.system_instructions)],
            )
            self.config = types.GenerateContentConfig(
                system_instruction=system_instructions_contents,
                tools=[types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER,
                        # TODO: Hardcoding for now, but should pass in from init
                        excluded_predefined_functions=self.excluded_functions
                    )
                )],
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE)
                ]
            )
        else:
            self.config = types.GenerateContentConfig(
                tools=[types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER,
                        # TODO: Hardcoding for now, but should pass in from init
                        excluded_predefined_functions=self.excluded_functions
                    )
                )],
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE)
                ]
            )

    # TODO: add type hint for initial_image
    def build_initial_message(self, goal: str, initial_image):
        """Build the initial message for llm"""
        return [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=goal),
                    # TODO: check mime_type instead of hardcoding here
                    types.Part.from_bytes(data=initial_image, mime_type="image/png"),
                ],
            )
        ]

    @time_logger
    def generate_content(self, contents: List[types.Content]):
        """Generate response from llm"""
        response = self.gemini_client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=self.config
        )

        return response
    
    @time_logger
    async def generate_content_async(self, contents: List[types.Content]):
        """Generate response from llm using aio client"""
        response = await self.gemini_client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=self.config
        )

        return response

    # TODO: add type hint for screenshot
    def build_function_responses_message(self,
                                         screenshot,
                                         current_url: str,
                                         results: List[tuple[str, Dict[str, Any]]]) -> types.Content:
        """Build the functions response for each run in the loop"""
        function_responses = []
        for name, result in results:
            response_data = {"url": current_url}
            response_data.update(result)
            function_responses.append(
                types.FunctionResponse(
                    name=name,
                    response=response_data,
                    parts=[
                        types.FunctionResponsePart(
                            inline_data=types.FunctionResponseBlob(
                                # TODO: check mime_type instead of hardcoding here
                                mime_type="image/png",
                                data=screenshot
                            )
                        )
                    ]
                )
            )
        
        return types.Content(
            role="user",
            parts=[
                types.Part(function_response=function_response)
                for function_response in function_responses
            ]
        )
