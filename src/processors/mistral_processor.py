from .base_processor import BaseLLMProcessor
from .registry import ProcessorRegistry
from typing import Dict, Any
import os
import requests
import json
from dotenv import load_dotenv

@ProcessorRegistry.register("mistral")
class MiniMaxProcessor(BaseLLMProcessor):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model_name = "x-ai/grok-2-1212"
        
    def process(self, tweet: str, prompt_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Process a tweet using MiniMax API via OpenRouter
        
        Args:
            tweet: The tweet content to process
            prompt_data: Dictionary containing prompt templates and examples
            kwargs: Additional arguments
        """
        # Get prompt type from kwargs or use default
        prompt_type = kwargs.get('prompt_type', 'default')
        
        # Prepare messages for the API call
        messages = self.format_messages(tweet, prompt_data)
        
        # Prepare headers and payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "x-ai/grok-2-1212",
            "messages": messages
        }
        
        try:
            # Make API call
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            response_text = response_data["choices"][0]["message"]["content"]
            
        except Exception as e:
            response_text = f"Error calling MiniMax API: {str(e)}"
        
        return self.get_result_dict(tweet, prompt_type, messages, response_text) 