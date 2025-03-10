from .base_processor import BaseLLMProcessor
from .registry import ProcessorRegistry
from typing import Dict, Any
import os
import requests
import json
from dotenv import load_dotenv

@ProcessorRegistry.register("base-4o-mini")
class Base4oMiniProcessor(BaseLLMProcessor):
    def __init__(self):
        super().__init__()
        load_dotenv()
        # Get Azure OpenAI credentials from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.model_name = os.getenv("AZURE_OPENAI_MODEL", "base-4o-mini")
        self.temperature = float(os.getenv("AZURE_OPENAI_TEMPERATURE", 0))
        
    def process(self, tweet: str, prompt_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Process a tweet using the provided prompt data
        
        Args:
            tweet: The tweet content to process
            prompt_data: Dictionary containing prompt templates and examples
            kwargs: Additional arguments
            
        Returns:
            Dictionary with processing results
        """
        # Get prompt type from kwargs or use default
        prompt_type = kwargs.get('prompt_type', 'default')
        
        # Prepare messages for the API call
        messages = self.format_messages(tweet, prompt_data)
        
        # Construct the API URL
        url = f"{self.endpoint}openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        
        # Prepare the request headers and payload
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "messages": messages,
            "temperature": self.temperature
        }
        
        # Make the API call
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the response
            response_data = response.json()
            response_text = response_data["choices"][0]["message"]["content"]
            
        except Exception as e:
            response_text = f"Error calling Azure OpenAI API: {str(e)}"
        
        return self.get_result_dict(tweet, prompt_type, messages, response_text) 