import json
import os
import webbrowser
import argparse
import concurrent.futures
from datetime import datetime
import sys

# Import the processors package first to ensure registration occurs
import processors
from processors import ProcessorRegistry
from report_generator import ReportGenerator
from config_manager import ConfigManager

def load_data(tweets_file='data/tweets.json', config_manager=None):
    """Load tweets and prompt data."""
    # Load tweets
    with open(tweets_file, 'r', encoding='utf-8') as f:
        tweets_data = json.load(f)
        tweets = [tweet_data['tweet_content'] for tweet_data in tweets_data]
    
    # Load prompts using config manager
    if config_manager:
        prompt_files = config_manager.get_prompt_files()
        prompts_data = config_manager.load_prompt_files(prompt_files)
    else:
        prompts_data = {}
    
    return tweets, prompts_data, tweets_data

def ensure_output_dir():
    """Ensure the output directory exists"""
    if not os.path.exists('output'):
        os.makedirs('output')

def process_tweet_with_processor(args):
    """Process a single tweet with a single processor"""
    tweet, tweet_data, processor, prompt_data, kwargs = args
    
    # Add tweet metadata to kwargs for processors that might use it
    processor_kwargs = kwargs.copy()
    processor_kwargs.update({
        'username': tweet_data.get('username', ''),
        'tweet_id': tweet_data.get('tweet_id', ''),
        'user_id': tweet_data.get('user_id', '')
    })
    
    try:
        return processor.process(tweet, prompt_data, **processor_kwargs)
    except Exception as e:
        processor_type = type(processor).__name__
        print(f"Error processing tweet with {processor_type}: {e}")
        return {
            'tweet': tweet,
            'prompt_type': kwargs.get('prompt_type', 'unknown'),
            'llm_model': getattr(processor, 'model_name', 'unknown'),
            'prompt': str(prompt_data),
            'response': f"Error processing: {str(e)}"
        }

def main():
    parser = argparse.ArgumentParser(description='Process tweets with different LLM processors')
    parser.add_argument('tweets_file', nargs='?', default='data/tweets.json',
                        help='Path to the JSON file containing tweets (default: data/tweets.json)')
    parser.add_argument('--config', default='config.json',
                        help='Path to configuration file (default: config.json)')
    parser.add_argument('--max-workers', type=int, default=4,
                        help='Maximum number of worker threads (default: 4)')
    parser.add_argument('--list-processors', action='store_true',
                        help='List all available processors and exit')
    args = parser.parse_args()
    
    # If --list-processors is specified, print available processors and exit
    if args.list_processors:
        print("Available processors:")
        for name in ProcessorRegistry.list_available_processors():
            print(f"  - {name}")
        sys.exit(0)
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    
    # Load data
    tweets, prompts_data, tweets_data = load_data(args.tweets_file, config_manager)
    ensure_output_dir()
    
    # Get the base filename without extension for the report
    tweets_filename = os.path.basename(args.tweets_file)
    tweets_basename = os.path.splitext(tweets_filename)[0]
    
    # Initialize processors based on configuration
    processors = []
    processor_configs = config_manager.get_processor_configurations()
    
    if not processor_configs:
        # Use default processors if none configured
        print("No processors configured, using defaults...")
        processors = [
            (ProcessorRegistry.get_processor("base-4o-mini"), 
             prompts_data.get('social', {}), 
             {'prompt_type': 'social_media'})
        ]
    else:
        # Initialize processors from configuration
        for config in processor_configs:
            processor_name = config.get('name')
            prompt_type = config.get('prompt_type')
            prompt_key = config.get('prompt_key')
            
            if not all([processor_name, prompt_type, prompt_key]):
                print(f"Skipping invalid processor configuration: {config}")
                continue
                
            try:
                processor = ProcessorRegistry.get_processor(processor_name)
                prompt_data = prompts_data.get(prompt_key, {})
                kwargs = {'prompt_type': prompt_type}
                # Add any additional configuration
                kwargs.update(config.get('additional_config', {}))
                
                processors.append((processor, prompt_data, kwargs))
            except Exception as e:
                print(f"Error initializing processor {processor_name}: {e}")
    
    # Create a list of all tasks to be processed in parallel
    tasks = []
    for i, tweet in enumerate(tweets):
        tweet_data = tweets_data[i]
        for processor, prompt_data, kwargs in processors:
            tasks.append((tweet, tweet_data, processor, prompt_data, kwargs))
    
    results = []
    
    # Process all tasks in parallel
    print(f"Processing {len(tweets)} tweets with {len(processors)} processors using {args.max_workers} workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit all tasks and collect results as they complete
        future_to_task = {executor.submit(process_tweet_with_processor, task): task for task in tasks}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_task):
            try:
                result = future.result()
                results.append(result)
                # Print progress
                print(f"Processed {len(results)}/{len(tasks)} tasks", end='\r')
            except Exception as exc:
                task = future_to_task[future]
                tweet = task[0]
                processor_type = type(task[2]).__name__
                print(f"Task for tweet '{tweet[:30]}...' with {processor_type} generated an exception: {exc}")
    
    print(f"\nCompleted processing {len(results)} tasks.")
    
    # Generate report
    report_generator = ReportGenerator()
    report_html = report_generator.generate_report(results)
    
    # Create a timestamped filename that includes the tweets file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"output/report_{tweets_basename}_{timestamp}.html"
    
    # Save the report
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    # Create a symlink or copy to latest report for convenience
    latest_report = f"output/latest_{tweets_basename}_report.html"
    if os.path.exists(latest_report):
        os.remove(latest_report)
    
    # Create a copy of the latest report
    with open(latest_report, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    # Open the report in the default browser
    report_path = os.path.abspath(report_filename)
    webbrowser.open('file://' + report_path)
    
    print(f"Processed {len(tweets)} tweets from {args.tweets_file} with {len(processors)} processors.")
    print(f"Generated report saved to {report_filename}")
    print(f"Report opened in your default browser")

if __name__ == "__main__":
    main() 