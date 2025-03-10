from typing import Dict, Any
import os
from dotenv import load_dotenv
import json

load_dotenv()

class BaseLLMProcessor:
    """Base class for all LLM processors."""
    
    def __init__(self):
        # Common initialization
        self.model_name = "base-model"
    
    def process(self, tweet: str, prompt_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Base method to be implemented by child classes
        
        Args:
            tweet: The tweet content to process
            prompt_data: Dictionary containing prompt templates and examples
            **kwargs: Additional arguments that may include:
                - username: The username of the tweet author
                - tweet_id: The ID of the tweet
                - user_id: The ID of the user
                - prompt_type: Type of prompt used
                - Other processor-specific arguments
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_messages(self, tweet: str, prompt_data: Dict) -> list:
        """Format messages for the API call based on prompt data."""
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
        
        return messages
    
    def get_result_dict(self, tweet: str, prompt_type: str, messages: list, response_text: str) -> Dict[str, Any]:
        """Create a standardized result dictionary."""
        return {
            'tweet': tweet,
            'prompt_type': prompt_type,
            'llm_model': self.model_name,
            'prompt': json.dumps(messages, indent=2),
            'response': response_text
        }