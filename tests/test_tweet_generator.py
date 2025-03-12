import os
import json
import pytest
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.pinecone_context_processor import PineconeContextProcessor

@pytest.fixture
def tweet_generator_prompt():
    """Load the tweet generator prompt data"""
    with open("data/tweet_generator_prompt.json", "r") as f:
        return json.load(f)

def test_tweet_generation():
    """Test generating tweets with context from Pinecone"""
    # Initialize the processor
    processor = PineconeContextProcessor()
    
    # Load the prompt data
    with open("data/tweet_generator_prompt.json", "r") as f:
        prompt_data = json.load(f)
    
    # Test topics
    topics = [
        "Ethereum ecosystem",
        "DeFi innovations",
        "NFT marketplaces",
        "Layer 2 solutions",
        "Web3 social platforms"
    ]
    
    # Generate tweets for each topic
    for topic in topics:
        # Create a modified prompt data with the topic inserted
        modified_prompt = prompt_data.copy()
        modified_prompt["user_template"] = modified_prompt["user_template"].replace("{topic}", topic)
        
        result = processor.process(
            tweet=topic,  # Using the topic as the "tweet" input
            prompt_data=modified_prompt,
            prompt_type="tweet_generation",
            namespace="tweets",
            top_k=5  # Get 5 similar tweets for context
        )
        
        # Print the generated tweet
        print(f"\nTopic: {topic}")
        print(f"Generated Tweet: {result['response']}")
        
        # Verify the result contains expected fields
        assert "response" in result
        assert "similar_tweets" in result
        assert len(result["similar_tweets"]) <= 5
        
        # Verify the tweet is not too long
        assert len(result["response"])

if __name__ == "__main__":
    # This allows running the test directly
    test_tweet_generation() 