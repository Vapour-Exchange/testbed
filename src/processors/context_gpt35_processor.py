from .base_processor import BaseLLMProcessor
from typing import Dict, Any

class ContextGPT35Processor(BaseLLMProcessor):
    def process(self, tweet: str, prompt_template: str, **kwargs) -> Dict[str, Any]:
        context = kwargs.get('context', '')
        prompt = prompt_template.format(tweet=tweet, context=context)
        
        # Static response for testing
        response = f"This is a static response from ContextGPT35Processor analyzing: '{tweet}' with context: '{context}'"
        
        return {
            'tweet': tweet,
            'prompt_type': 'with_context',
            'llm_model': 'gpt-3.5',
            'prompt': prompt,
            'response': response
        } 