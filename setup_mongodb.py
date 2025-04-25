import pymongo
import os
import logging
import subprocess
import sys
import time
from pymongo.errors import ConnectionFailure

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_mongodb_running():
    """Check if MongoDB is running"""
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return True
    except Exception:
        return False

def start_mongodb():
    """Attempt to start MongoDB if it's installed"""
    try:
        # Check if MongoDB is installed
        result = subprocess.run(["which", "mongod"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning("MongoDB is not installed. Please install MongoDB to use all features.")
            return False
        
        # Try to start MongoDB
        logger.info("Attempting to start MongoDB...")
        subprocess.Popen(["mongod", "--dbpath", "/tmp/mongodb"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for MongoDB to start
        for i in range(5):
            if check_mongodb_running():
                logger.info("MongoDB started successfully")
                return True
            time.sleep(2)
        
        logger.warning("Failed to start MongoDB")
        return False
    except Exception as e:
        logger.error(f"Error starting MongoDB: {e}")
        return False

def setup_mongodb():
    """Set up MongoDB database and collections"""
    # Check if MongoDB is running
    if not check_mongodb_running():
        # Try to start MongoDB
        if not start_mongodb():
            logger.warning("Using fallback storage. Some features may be limited.")
            return False
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        
        # Create database
        db = client["philosophy_ai"]
        
        # Create collections
        chat_messages = db["chat_messages"]
        
        # Create indexes
        chat_messages.create_index([("session_id", pymongo.ASCENDING)])
        chat_messages.create_index([("user_id", pymongo.ASCENDING)])
        chat_messages.create_index([("timestamp", pymongo.ASCENDING)])
        
        logger.info("MongoDB setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"MongoDB setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_mongodb()