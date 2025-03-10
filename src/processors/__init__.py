"""
Processors package initialization.
This file ensures all processor implementations are imported.
"""

from .registry import ProcessorRegistry
from .base_processor import BaseLLMProcessor

# Import all processor implementations so their decorators run
# and they register themselves in the ProcessorRegistry
import importlib
import os
import pkgutil

# Automatically import all modules in the processors package
__all__ = ['ProcessorRegistry', 'BaseLLMProcessor']

# Discover and import all modules in this package to ensure decorators run
package_dir = os.path.dirname(__file__)
for (_, module_name, _) in pkgutil.iter_modules([package_dir]):
    # Skip importing this init module to avoid circular imports
    if module_name != "__init__":
        # Import the module to trigger the decorators
        importlib.import_module(f"{__name__}.{module_name}")
        __all__.append(module_name)

# Print registered processors for debugging
print(f"Registered processors: {', '.join(ProcessorRegistry.list_available_processors()) or 'none'}") 