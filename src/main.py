import json
import os
import webbrowser
import argparse
from datetime import datetime
from llm_processor import SimpleGPT4Processor, ContextGPT35Processor, FewShotGPT4Processor
from report_generator import ReportGenerator

def load_data(tweets_file='data/tweets.json'):
    with open(tweets_file, 'r', encoding='utf-8') as f:
        tweets_data = json.load(f)
        # Extract tweet content from the full tweet data
        tweets = [tweet_data['tweet_content'] for tweet_data in tweets_data]
    
    with open('data/prompts.json', 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    return tweets, prompts, tweets_data

def ensure_output_dir():
    """Ensure the output directory exists"""
    if not os.path.exists('output'):
        os.makedirs('output')

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process tweets with different LLM processors')
    parser.add_argument('tweets_file', nargs='?', default='data/tweets.json',
                        help='Path to the JSON file containing tweets (default: data/tweets.json)')
    args = parser.parse_args()
    
    # Load data from the specified file
    tweets, prompts, tweets_data = load_data(args.tweets_file)
    ensure_output_dir()
    
    # Get the base filename without extension for the report
    tweets_filename = os.path.basename(args.tweets_file)
    tweets_basename = os.path.splitext(tweets_filename)[0]
    
    # Initialize processors
    processors = [
        (SimpleGPT4Processor(), prompts['simple_template'], {}),
        (ContextGPT35Processor(), prompts['context_template'], 
         {'context': prompts['additional_context']}),
        (FewShotGPT4Processor(), prompts['few_shot_template'], 
         {'examples': prompts['examples']})
    ]
    
    results = []
    
    # Process tweets with each processor
    for i, tweet in enumerate(tweets):
        # Get the full tweet data for additional context
        tweet_data = tweets_data[i]
        
        for processor, template, kwargs in processors:
            # Add tweet metadata to kwargs for processors that might use it
            processor_kwargs = kwargs.copy()
            processor_kwargs.update({
                'username': tweet_data['username'],
                'tweet_id': tweet_data['tweet__id'],
                'user_id': tweet_data['user_id']
            })
            
            result = processor.process(tweet, template, **processor_kwargs)
            results.append(result)
    
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