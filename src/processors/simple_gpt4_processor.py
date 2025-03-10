from .base_processor import BaseLLMProcessor
from typing import Dict, Any

class SimpleGPT4Processor(BaseLLMProcessor):
    def process(self, tweet: str, prompt_template: str, **kwargs) -> Dict[str, Any]:
        prompt = prompt_template.format(tweet=tweet)
        
        # Static response for testing
        response = f"This is a static response from SimpleGPT4Processor analyzing: '{tweet}'"
        
        return {
            'tweet': tweet,
            'prompt_type': 'simple',
            'llm_model': 'gpt-4',
            'prompt': prompt,
            'response': response
        } 