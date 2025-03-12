import os
import csv
import argparse
import time
from typing import List, Dict, Any
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
import sys

# Load environment variables
load_dotenv()

# Try to import the correct Pinecone package
try:
    from pinecone import Pinecone
except ImportError:
    print("Error: The 'pinecone' package is not installed.")
    print("Please install it with: pip install --upgrade pinecone")
    sys.exit(1)

class PineconeUploader:
    """
    Utility for uploading tweets to a Pinecone vector database using the upsert_records method.
    This allows for semantic search and retrieval of tweets.
    """
    
    def __init__(self, api_key=None, index_host=None):
        """
        Initialize the Pinecone uploader with API credentials.
        
        Args:
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env var)
            index_host: Pinecone index host (defaults to PINECONE_INDEX_HOST env var)
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_host = index_host or os.getenv("PINECONE_INDEX_HOST")
        
        # Reduce batch size to 96 (Pinecone's limit) or less
        self.batch_size = 50  # Reduced from 100 to stay well under the limit
        self.namespace = "tweets"  # Namespace for storing tweets
        
        if not all([self.api_key, self.index_host]):
            raise ValueError("Missing Pinecone credentials. Set PINECONE_API_KEY and PINECONE_INDEX_HOST environment variables or provide as parameters.")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(host=self.index_host)
    
    def parse_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        Parse the CSV file containing tweets.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            List of dictionaries containing tweet data
        """
        tweets = []
        
        try:
            # Read the CSV file with proper headers
            df = pd.read_csv(csv_path)
            
            # Check if the CSV has the expected columns
            if 'tweet_content' in df.columns:
                # Process each row
                for _, row in df.iterrows():
                    tweet_data = {
                        'content': row['tweet_content'],
                        'username': row.get('username', ''),
                        'tweet_id': str(row.get('tweet__id', '')).strip('"'),
                        'user_id': str(row.get('user_id', '')).strip('"')
                    }
                    tweets.append(tweet_data)
            else:
                # Try to infer columns
                print("Warning: Expected column 'tweet_content' not found. Trying to infer columns.")
                
                # Assume first column is tweet content if it has more than 2 columns
                if len(df.columns) >= 2:
                    for _, row in df.iterrows():
                        tweet_data = {
                            'content': row[df.columns[0]],
                            'username': row[df.columns[1]] if len(df.columns) > 1 else '',
                            'tweet_id': str(row[df.columns[2]]) if len(df.columns) > 2 else '',
                            'user_id': str(row[df.columns[3]]) if len(df.columns) > 3 else ''
                        }
                        tweets.append(tweet_data)
                else:
                    # If only one column, assume it's all tweet content
                    for _, row in df.iterrows():
                        tweet_data = {
                            'content': row[df.columns[0]],
                            'username': '',
                            'tweet_id': '',
                            'user_id': ''
                        }
                        tweets.append(tweet_data)
        
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            
            # Try as a simple text file, one tweet per line
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        tweet_data = {
                            'content': line.strip(),
                            'username': '',
                            'tweet_id': str(i),
                            'user_id': ''
                        }
                        tweets.append(tweet_data)
            except Exception as e2:
                print(f"Error parsing as text file: {e2}")
                return []
        
        return tweets
    
    def upload_to_pinecone(self, tweets: List[Dict[str, Any]]) -> None:
        """
        Upload tweets to Pinecone index using upsert_records.
        
        Args:
            tweets: List of tweet dictionaries
        """
        total_batches = (len(tweets) - 1) // self.batch_size + 1
        
        # Process in batches
        for i in range(0, len(tweets), self.batch_size):
            batch = tweets[i:i+self.batch_size]
            
            # Format records for upsert_records
            records = []
            for j, tweet in enumerate(batch):
                # Generate a unique ID
                tweet_id = tweet.get('tweet_id', '')
                if not tweet_id:
                    tweet_id = f"{i+j}"
                
                record = {
                    "_id": f"tweet_{tweet_id}",
                    "text": tweet['content'],  # Changed from 'chunk_text' to 'text'
                    "username": tweet.get('username', ''),
                    "user_id": tweet.get('user_id', ''),
                    "tweet_id": tweet_id
                }
                records.append(record)
            
            # Upload to Pinecone using upsert_records
            print(f"Uploading batch {i//self.batch_size + 1}/{total_batches} to Pinecone ({len(records)} records)")
            try:
                self.index.upsert_records(
                    namespace=self.namespace,
                    records=records
                )
                print(f"Successfully uploaded batch {i//self.batch_size + 1}/{total_batches}")
            except Exception as e:
                print(f"Error uploading batch {i//self.batch_size + 1}/{total_batches}: {e}")
                # If batch is still too large, try with a smaller batch
                if "Batch size exceeds" in str(e):
                    half_size = len(records) // 2
                    print(f"Trying with smaller batch size of {half_size}")
                    try:
                        self.index.upsert_records(
                            namespace=self.namespace,
                            records=records[:half_size]
                        )
                        print(f"Successfully uploaded first half of batch {i//self.batch_size + 1}/{total_batches}")
                        
                        # Wait a moment before uploading the second half
                        time.sleep(1)
                        
                        self.index.upsert_records(
                            namespace=self.namespace,
                            records=records[half_size:]
                        )
                        print(f"Successfully uploaded second half of batch {i//self.batch_size + 1}/{total_batches}")
                    except Exception as e2:
                        print(f"Error uploading smaller batches: {e2}")
            
            # Respect rate limits
            time.sleep(1)
    
    def process_csv_file(self, csv_path: str) -> None:
        """
        Process a CSV file and upload tweets to Pinecone.
        
        Args:
            csv_path: Path to the CSV file
        """
        # Parse CSV
        tweets = self.parse_csv(csv_path)
        
        if not tweets:
            print("No tweets found in the CSV file.")
            return
        
        # Upload to Pinecone
        print(f"Uploading {len(tweets)} tweets to Pinecone index in namespace '{self.namespace}'")
        self.upload_to_pinecone(tweets)
        print("Upload complete!")

def main():
    parser = argparse.ArgumentParser(description='Upload tweets from CSV to Pinecone vector database')
    parser.add_argument('csv_file', help='Path to the CSV file containing tweets')
    parser.add_argument('--api-key', help='Pinecone API key (defaults to PINECONE_API_KEY env var)')
    parser.add_argument('--index-host', help='Pinecone index host (defaults to PINECONE_INDEX_HOST env var)')
    parser.add_argument('--namespace', help='Pinecone namespace (defaults to "tweets")')
    parser.add_argument('--batch-size', type=int, help='Number of records to upload in each batch (default: 50, max: 96)')
    
    args = parser.parse_args()
    
    try:
        uploader = PineconeUploader(
            api_key=args.api_key,
            index_host=args.index_host
        )
        
        if args.namespace:
            uploader.namespace = args.namespace
            
        if args.batch_size:
            if args.batch_size > 96:
                print("Warning: Batch size cannot exceed 96. Setting to 96.")
                uploader.batch_size = 96
            else:
                uploader.batch_size = args.batch_size
                
        uploader.process_csv_file(args.csv_file)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 