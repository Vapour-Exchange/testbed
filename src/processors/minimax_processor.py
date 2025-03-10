from .base_processor import BaseLLMProcessor
from typing import Dict, Any
import os
import requests
import json
from dotenv import load_dotenv

class MiniMaxProcessor(BaseLLMProcessor):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def process(self, tweet: str, prompt_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Process a tweet using MiniMax API via OpenRouter
        
        Args:
            tweet: The tweet content to process
            prompt_data: Dictionary containing prompt templates and examples
            kwargs: Additional arguments
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
        
        # Prepare headers and payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "minimax/minimax-01",
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
        
        return {
            'tweet': tweet,
            'prompt_type': 'social_media_comment',
            'llm_model': 'minimax-01',
            'prompt': json.dumps(messages, indent=2),
            'response': response_text
        } 