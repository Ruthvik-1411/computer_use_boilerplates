"""Encapsulate LLM (Gemini) interactions."""
from typing import List, Dict, Any
from google.genai import Client, types

class GeminiComputerUseClient:
    """Gemini client class"""

    def __init__(self,
                 api_key: str,
                 model_name: str = "gemini-2.5-computer-use-preview-10-2025",
                 system_instructions: str = ""):
        # Note: Pass in project id and location if using ADC
        self.gemini_client = Client(
            api_key=api_key
        )
        self.model_name = model_name
        self.system_instructions = system_instructions
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
                        excluded_predefined_functions=["drag_and_drop", "open_web_browser"]
                    )
                )],
                thinking_config=types.ThinkingConfig(include_thoughts=True),
            )
        else:
            self.config = types.GenerateContentConfig(
                tools=[types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER,
                        # TODO: Hardcoding for now, but should pass in from init
                        excluded_predefined_functions=["drag_and_drop", "open_web_browser"]
                    )
                )],
                thinking_config=types.ThinkingConfig(include_thoughts=True),
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

    def generate_content(self, contents: List[types.Content]):
        """Generate response from llm"""
        response = self.gemini_client.models.generate_content(
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
