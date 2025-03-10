import json
import os
import webbrowser
import argparse
import concurrent.futures
from datetime import datetime
from processors.base_4o_mini import Base4oMiniProcessor
from report_generator import ReportGenerator

def load_data(tweets_file='data/tweets.json', prompts_file='data/social_media_prompt.json'):
    with open(tweets_file, 'r', encoding='utf-8') as f:
        tweets_data = json.load(f)
        # Extract tweet content from the full tweet data
        tweets = [tweet_data['tweet_content'] for tweet_data in tweets_data]
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    
    return tweets, prompt_data, tweets_data

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
        'tweet_id': tweet_data.get('tweet__id', ''),
        'user_id': tweet_data.get('user_id', '')
    })
    
    return processor.process(tweet, prompt_data, **processor_kwargs)

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process tweets with different LLM processors')
    parser.add_argument('tweets_file', nargs='?', default='data/tweets.json',
                        help='Path to the JSON file containing tweets (default: data/tweets.json)')
    parser.add_argument('--prompts-file', default='data/social_media_prompt.json',
                        help='Path to the JSON file containing prompts (default: data/social_media_prompt.json)')
    parser.add_argument('--max-workers', type=int, default=4,
                        help='Maximum number of worker threads (default: 4)')
    args = parser.parse_args()
    
    # Load data from the specified files
    tweets, prompt_data, tweets_data = load_data(args.tweets_file, args.prompts_file)
    ensure_output_dir()
    
    # Get the base filename without extension for the report
    tweets_filename = os.path.basename(args.tweets_file)
    tweets_basename = os.path.splitext(tweets_filename)[0]
    
    # Initialize processors
    processors = [
        (Base4oMiniProcessor(), prompt_data, {}),
        # Add more processors here as needed
    ]
    
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