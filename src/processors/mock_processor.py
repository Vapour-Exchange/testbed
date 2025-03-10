from .base_processor import BaseLLMProcessor
from .registry import ProcessorRegistry
from typing import Dict, Any

@ProcessorRegistry.register("mock")
class MockProcessor(BaseLLMProcessor):
    """A mock processor for testing purposes that doesn't require API calls."""
    
    def __init__(self):
        super().__init__()
        self.model_name = "mock-model"
    
    def process(self, tweet: str, prompt_data: Dict, **kwargs) -> Dict[str, Any]:
        """Process a tweet with a mock response."""
        # Get prompt type from kwargs or use default
        prompt_type = kwargs.get('prompt_type', 'default')
        
        # Prepare messages for the API call
        messages = self.format_messages(tweet, prompt_data)
        
        # Generate a mock response
        response_text = f"Mock analysis of: '{tweet}'"
        
        return self.get_result_dict(tweet, prompt_type, messages, response_text) 