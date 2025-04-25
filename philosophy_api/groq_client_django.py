import os
import requests
import json
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GroqClient:
    """Client for interacting with Groq API"""
    
    def __init__(self):
        """Initialize the Groq client"""
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment variables.")
            raise ValueError("GROQ_API_KEY is required. Please set it in your environment variables.")
    
    def generate_response(self, messages):
        """Generate a response from the Groq API"""
        try:
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            # Make the request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract the content
            content = result["choices"][0]["message"]["content"]
            
            return content
        
        except Exception as e:
            logger.error(f"Error generating response from Groq API: {str(e)}")
            raise