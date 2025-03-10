# LLM Tweet Processor

This application processes tweets using various Language Model (LLM) processors to analyze content in different ways. It supports multiple LLM providers (Azure OpenAI, MiniMax, etc.) and can be configured to use different prompts and processor types.

## Features

- Process tweets with multiple LLM processors in parallel
- Dynamic processor registration system
- Configurable prompt templates
- Customizable processing pipeline
- HTML report generation comparing results

## Getting Started

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Configure your environment variables:

   - Create a `.env` file with your API keys (see `.env.example`)

3. Run the processor:

   ```
   python src/main.py data/tweets.json --config config.json
   ```

4. View the generated report in your browser (automatically opens)

## Documentation

- [Architecture Overview](architecture.md)
- [Processor System](processors.md)
- [Configuration](configuration.md)
- [Extending the System](extending.md)

## Requirements

- Python 3.8+
- Required packages: see requirements.txt
