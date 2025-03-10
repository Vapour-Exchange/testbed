from typing import Dict, Type, List
import inspect

class ProcessorRegistry:
    """Registry for LLM processors to enable dynamic loading and configuration."""
    
    _processors: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, name: str):
        """Decorator to register a processor class."""
        def decorator(processor_class):
            print(f"Registering processor: {name} from {inspect.getmodule(processor_class).__name__}")
            cls._processors[name] = processor_class
            return processor_class
        return decorator
    
    @classmethod
    def get_processor(cls, name: str):
        """Get an instance of a processor by name."""
        if name not in cls._processors:
            available = ", ".join(cls._processors.keys()) if cls._processors else "none"
            raise ValueError(f"Processor '{name}' not found in registry. Available processors: {available}")
        processor_class = cls._processors[name]
        return processor_class()
    
    @classmethod
    def list_available_processors(cls) -> List[str]:
        """Get a list of all registered processor names."""
        return list(cls._processors.keys()) 