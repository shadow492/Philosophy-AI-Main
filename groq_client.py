import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import time
import streamlit as st

# Try to load from .env file for local development
load_dotenv()

class GroqClient:
    def __init__(self):
        # First try to get API key from Streamlit secrets (for cloud deployment)
        # Then fall back to environment variables (for local development)
        self.api_key = st.secrets.get("GROQ_API_KEY", os.getenv('GROQ_API_KEY'))
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables or Streamlit secrets")
            
        # Initialize client with optimized configuration
        self.client = ChatGroq(
            groq_api_key=self.api_key,
            model_name='llama-3.3-70b-versatile',
            temperature=0.5,  # Lower temperature for more focused responses
            max_tokens=512,  # Limit response length 
        )
        
        # Initialize with buffer memory
        self.memory = ConversationBufferMemory()

    def generate_response(self, messages):
        """Generate response using full conversation history"""
        try:
            # Pass through messages exactly as received
            response = self.client.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            return "I need a moment to reflect. Please try your question again."

    def load_chat_history(self, messages):
        """
        Load previous chat history into memory
        """
        # Clear existing memory
        self.memory.clear()
        
        # Add each message pair to memory
        user_messages = [m for m in messages if m['role'] == 'user']
        assistant_messages = [m for m in messages if m['role'] == 'assistant']
        
        # Match user messages with assistant responses
        for i in range(min(len(user_messages), len(assistant_messages))):
            self.memory.save_context(
                {"input": user_messages[i]['content']}, 
                {"output": assistant_messages[i]['content']}
            )
                
        return True

    def summarize_conversation(self, messages):
        """Generate a summary of the conversation"""
        if not messages:
            return "Empty conversation"
            
        try:
            summary_prompt = [
                {'role': 'system', 'content': "You are Marcus Aurelius. Summarize this philosophical dialogue in your stoic voice, highlighting the key insights. Keep under 100 words."},
                {'role': 'user', 'content': '\n'.join([m['content'] for m in messages])}
            ]
            return self.generate_response(summary_prompt)
        except Exception as e:
            print(f"Summary generation error: {str(e)}")
            # Return a basic summary if generation fails
            return "A philosophical dialogue on the nature of wisdom and virtue."
        
    def health_check(self):
        """Check if the Groq API is working"""
        try:
            response = self.client.invoke([{"role": "user", "content": "Hello"}])
            return True
        except Exception as e:
            print(f"Health check failed: {str(e)}")
            return False