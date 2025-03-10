import json
import os
from typing import Dict, Any, List, Optional

class ConfigManager:
    """Manage configuration for the application."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize with optional config file path."""
        self.config = {}
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
    
    def load_prompt_files(self, prompts_config: Dict[str, str]) -> Dict[str, Any]:
        """Load prompt files based on configuration."""
        prompts_data = {}
        for prompt_name, prompt_file in prompts_config.items():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompts_data[prompt_name] = json.load(f)
            except Exception as e:
                print(f"Error loading prompt file {prompt_file}: {e}")
        return prompts_data
    
    def get_processor_configurations(self) -> List[Dict[str, Any]]:
        """Get configured processors from config."""
        return self.config.get("processors", [])
    
    def get_prompt_files(self) -> Dict[str, str]:
        """Get prompt file paths from config."""
        return self.config.get("prompt_files", {}) 