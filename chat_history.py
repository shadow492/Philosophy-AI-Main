from datetime import datetime
import json
import os
from pathlib import Path

# Define chat history directory
CHAT_HISTORY_DIR = Path("sessions")
CHAT_HISTORY_DIR.mkdir(exist_ok=True)

# Update the chat history directory
CHAT_HISTORY_DIR = Path("anonymous_sessions")
CHAT_HISTORY_DIR.mkdir(exist_ok=True)

def save_chat_session(session_data):
    """Save session with unique ID but never load it again"""
    filename = CHAT_HISTORY_DIR / f"{session_data['session_id']}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            'metadata': {
                'created_at': session_data.get('timestamp'),
                'philosopher': session_data['philosopher']
            },
            'messages': session_data['messages']
        }, f, indent=2)

# Remove load_chat_sessions and delete_chat_session functions
def load_chat_sessions(username):
    """Load all chat sessions for a user"""
    sessions = []
    user_dir = CHAT_HISTORY_DIR / username
    
    if not user_dir.exists():
        return sessions
        
    for file_path in user_dir.glob('*.json'):
        try:
            with open(file_path) as f:
                data = json.load(f)
                if not all(key in data for key in ['metadata', 'full_log']):
                    raise ValueError("Invalid session format")
                
                sessions.append({
                    'filename': file_path.name,
                    'timestamp': data['metadata']['created_at'],
                    'philosopher': data['metadata']['philosopher'],
                    'summary': data['metadata'].get('summary', ''),
                    'messages': data['full_log'],
                    'username': data['metadata']['username']
                })
        except Exception as e:
            print(f"Error loading session {file_path}: {e}")
    
    return sorted(sessions, key=lambda x: x['timestamp'], reverse=True)

def delete_chat_session(username, filename):
    """Delete a chat session"""
    user_dir = CHAT_HISTORY_DIR / username
    file_path = user_dir / filename
    
    if file_path.exists():
        os.remove(file_path)
        return True
    return False