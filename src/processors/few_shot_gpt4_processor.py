from .base_processor import BaseLLMProcessor
from typing import Dict, Any

class FewShotGPT4Processor(BaseLLMProcessor):
    def process(self, tweet: str, prompt_template: str, **kwargs) -> Dict[str, Any]:
        examples = kwargs.get('examples', [])
        examples_text = "\n".join([f"Tweet: {ex['tweet']}\nResponse: {ex['response']}" 
                                 for ex in examples])
        prompt = prompt_template.format(examples=examples_text, tweet=tweet)
        
        # Static response for testing
        response = f"This is a static response from FewShotGPT4Processor analyzing: '{tweet}' with {len(examples)} examples"
        
        return {
            'tweet': tweet,
            'prompt_type': 'few_shot',
            'llm_model': 'gpt-4',
            'prompt': prompt,
            'response': response
        } 