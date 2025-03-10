from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class BaseLLMProcessor:
    def __init__(self):
        # In a real implementation, we would set up API keys here
        pass
    
    def process(self, tweet: str, prompt_template: str, **kwargs) -> Dict[str, Any]:
        """
        Base method to be implemented by child classes
        
        Args:
            tweet: The tweet content to process
            prompt_template: The template string for the prompt
            **kwargs: Additional arguments that may include:
                - username: The username of the tweet author
                - tweet_id: The ID of the tweet
                - user_id: The ID of the user
                - Other processor-specific arguments
        """
        raise NotImplementedError ("Subclasses must implement this method")