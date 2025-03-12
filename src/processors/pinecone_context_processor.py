from .base_processor import BaseLLMProcessor
from .registry import ProcessorRegistry
from typing import Dict, Any, List
import os
import requests
import json
from dotenv import load_dotenv
from pinecone import Pinecone

@ProcessorRegistry.register("pinecone-context")
class PineconeContextProcessor(BaseLLMProcessor):
    def __init__(self):
        super().__init__()
        load_dotenv()
        
        # Azure OpenAI credentials for LLM
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.model_name = os.getenv("AZURE_OPENAI_MODEL", "base-4o-mini")
        self.temperature = float(os.getenv("AZURE_OPENAI_TEMPERATURE", 0))
        
        # Pinecone credentials
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_host = os.getenv("PINECONE_INDEX_HOST")
        self.pinecone_namespace = "tweets"  # Default namespace
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = self.pc.Index(host=self.pinecone_index_host)
        
        # Configuration
        self.top_k = 3  # Number of similar tweets to retrieve
    
    def find_similar_tweets(self, tweet_text: str) -> List[Dict]:
        """
        Find similar tweets in Pinecone using the given tweet text.
        
        Args:
            tweet_text: The tweet text to search with
            
        Returns:
            A list of dictionaries containing similar tweets and their metadata
        """
        try:
            # Use search_records to find similar tweets
            results = self.index.search_records(
                namespace=self.pinecone_namespace,
                query={
                    "inputs": {"text": tweet_text},
                    "top_k": self.top_k
                },
                fields=["text", "username", "user_id", "tweet_id"]
            )
            
            similar_tweets = []
            for hit in results.result.hits:
                similar_tweets.append({
                    'content': hit.fields.get('text', ''),
                    'username': hit.fields.get('username', ''),
                    'user_id': hit.fields.get('user_id', ''),
                    'tweet_id': hit.fields.get('tweet_id', ''),
                    'score': hit._score
                })
            
            return similar_tweets
            
        except Exception as e:
            print(f"Error querying Pinecone: {str(e)}")
            return []
    
    def format_context_messages(self, tweet: str, prompt_data: Dict, similar_tweets: List[Dict]) -> list:
        """
        Format messages for the API call, including similar tweets as context.
        
        Args:
            tweet: The tweet to process
            prompt_data: Dictionary containing prompt templates
            similar_tweets: List of similar tweets to use as context
            
        Returns:
            A list of message dictionaries for the API call
        """
        messages = []
        
        # Add system message if available
        if "system_template" in prompt_data:
            system_content = prompt_data["system_template"]
        else:
            system_content = "You are an AI assistant that analyzes tweets based on similar tweets in the database."
        
        messages.append({
            "role": "system", 
            "content": system_content
        })
        
        # Add context about similar tweets
        context = "Here are some similar tweets from our database:\n\n"
        for i, similar_tweet in enumerate(similar_tweets):
            context += f"{i+1}. Tweet by @{similar_tweet['username']} (similarity score: {similar_tweet['score']:.4f}): \"{similar_tweet['content']}\"\n"
        
        # Add examples if available
        if "examples" in prompt_data:
            for example in prompt_data["examples"]:
                messages.append({"role": "user", "content": example["user"]})
                messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add the context and current tweet as user message
        user_template = prompt_data.get("user_template", "Analyze this tweet: {tweet}")
        user_content = f"{context}\n\nNow, {user_template.format(tweet=tweet)}"
        messages.append({"role": "user", "content": user_content})
        
        return messages
    
    def process(self, tweet: str, prompt_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Process a tweet using similar tweets from Pinecone as context.
        
        Args:
            tweet: The tweet content to process
            prompt_data: Dictionary containing prompt templates and examples
            kwargs: Additional arguments
            
        Returns:
            Dictionary with processing results
        """
        # Get prompt type from kwargs or use default
        prompt_type = kwargs.get('prompt_type', 'default')
        
        # Override namespace if provided
        if 'namespace' in kwargs:
            self.pinecone_namespace = kwargs['namespace']
            
        # Override top_k if provided
        if 'top_k' in kwargs:
            self.top_k = kwargs['top_k']
        
        # Find similar tweets in Pinecone using the tweet text directly
        similar_tweets = self.find_similar_tweets(tweet)
        
        # Prepare messages for the API call, including similar tweets as context
        messages = self.format_context_messages(tweet, prompt_data, similar_tweets)
        
        # Construct the API URL for Azure OpenAI
        url = f"{self.endpoint}openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        
        # Prepare the request headers and payload
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        print(messages)
        payload = {
            "messages": messages,
            "temperature": self.temperature
        }
        
        # Make the API call
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            response_text = response_data["choices"][0]["message"]["content"]
            
        except Exception as e:
            response_text = f"Error calling Azure OpenAI API: {str(e)}"
        
        # Add similar tweets to the result for transparency
        result = self.get_result_dict(tweet, prompt_type, messages, response_text)
        result['similar_tweets'] = similar_tweets
        
        return result 