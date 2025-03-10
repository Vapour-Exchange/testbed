from .base_processor import BaseLLMProcessor
from typing import Dict, Any, List
import os
import requests
import json
from dotenv import load_dotenv

class Base4oMiniProcessor(BaseLLMProcessor):
    def __init__(self):
        load_dotenv()
        # Get Azure OpenAI credentials from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.model = os.getenv("AZURE_OPENAI_MODEL")
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
        # Prepare messages for the API call
        messages = []
        
        # Add system message if available
        if "system_template" in prompt_data:
            messages.append({
                "role": "system", 
                "content": prompt_data["system_template"]
            })
        
        # Add examples if available
        if "examples" in prompt_data:
            for example in prompt_data["examples"]:
                messages.append({"role": "user", "content": example["user"]})
                messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add the current tweet as user message
        user_content = prompt_data.get("user_template", "{tweet}").format(tweet=tweet)
        messages.append({"role": "user", "content": user_content})
        
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
        
        return {
            'tweet': tweet,
            'prompt_type': 'social_media_comment',
            'llm_model': self.model,
            'prompt': json.dumps(messages, indent=2),
            'response': response_text
        } 