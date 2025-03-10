# Architecture Overview

The LLM Tweet Processor is built with a modular, extensible architecture focused on processing flexibility and ease of extension.

## Core Components

![Architecture Diagram](https://via.placeholder.com/800x400?text=Architecture+Diagram)

### Main Components

1. **Processor Registry**

   - Central system for registering and retrieving processor implementations
   - Allows dynamic discovery of available processors

2. **Base Processor**

   - Abstract base class defining the processor interface
   - Provides common utilities for all processors

3. **Specialized Processors**

   - Concrete implementations for different LLM providers (Azure OpenAI, MiniMax, etc.)
   - Each processor handles provider-specific API communication

4. **Configuration Manager**

   - Manages application configuration from JSON files
   - Handles loading prompt templates and processor settings

5. **Report Generator**
   - Creates HTML reports comparing results from different processors
   - Organizes results by tweet and processor for easy comparison

## Processing Flow

1. User invokes the main script with configuration parameters
2. System loads tweets and configuration
3. For each tweet and processor combination:
   - Formats appropriate prompts based on configuration
   - Sends request to the corresponding LLM API
   - Collects and stores responses
4. Results are compiled into a comparative HTML report
5. Report is displayed in the default browser

## Parallel Processing

The system uses Python's `concurrent.futures` to process multiple tweets across multiple processors in parallel, significantly improving throughput for batch processing.
