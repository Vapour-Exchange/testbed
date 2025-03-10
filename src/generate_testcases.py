import csv
import json
import random
import os

def generate_test_tweets(csv_file='data/tweets.csv', output_file='data/tweets.json', num_tweets=20):
    """
    Generate test cases by randomly selecting tweets from a CSV file.
    Preserves all columns from the CSV in the JSON output.
    
    Args:
        csv_file: Path to the CSV file containing tweets
        output_file: Path to save the selected tweets as JSON
        num_tweets: Number of tweets to select
    """
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Read tweets from CSV
    tweets = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweets.append(row)
    
    # Check if we have enough tweets
    if len(tweets) < num_tweets:
        print(f"Warning: CSV contains only {len(tweets)} tweets, using all of them.")
        selected_tweets = tweets
    else:
        # Randomly select tweets
        selected_tweets = random.sample(tweets, num_tweets)
    
    # Save selected tweets to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(selected_tweets, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully generated {len(selected_tweets)} test tweets and saved to {output_file}")
    return selected_tweets

if __name__ == "__main__":
    tweets = generate_test_tweets()
    
    # Print a preview of the selected tweets
    print("\nPreview of selected tweets:")
    for i, tweet in enumerate(tweets[:5], 1):
        # Truncate long tweets for display
        preview = tweet['tweet_content'][:100] + "..." if len(tweet['tweet_content']) > 100 else tweet['tweet_content']
        print(f"{i}. {preview}")
        print(f"   Username: {tweet['username']}, Tweet ID: {tweet['tweet__id']}")
    
    if len(tweets) > 5:
        print(f"... and {len(tweets) - 5} more tweets") 