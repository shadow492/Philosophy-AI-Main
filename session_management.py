from datetime import datetime
import json
from pathlib import Path
from chat_history import CHAT_HISTORY_DIR

def create_session(philosopher_id, username):
    """Create a new chat session"""
    return {
        'timestamp': datetime.now().isoformat(),
        'philosopher': philosopher_id,
        'messages': [],
        'summary': None,
        'username': username,
        'filename': None
    }

def save_session(session_data, summary_generator):
    """Save the current chat session"""
    # Create user directory if it doesn't exist
    user_dir = CHAT_HISTORY_DIR / session_data['username']
    user_dir.mkdir(exist_ok=True)
    
    # Get first user message for session name
    first_message = "untitled"
    for msg in session_data['messages']:
        if msg['role'] == 'user':
            first_message = msg['content'][:20].replace(" ", "_")
            break
    
    # Generate summary if needed
    if not session_data['summary'] and summary_generator and len(session_data['messages']) > 0:
        session_data['summary'] = summary_generator(session_data['messages'])
    
    # If session has a filename, use it (for updating existing sessions)
    if 'filename' in session_data and session_data['filename']:
        filename = user_dir / session_data['filename']
    else:
        # Create new filename for new sessions
        filename = user_dir / f"{first_message}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            'metadata': {
                'created_at': str(datetime.now()),
                'philosopher': session_data['philosopher'],
                'summary': session_data['summary'],
                'username': session_data['username']
            },
            'checkpoints': session_data['messages'][::5] + [session_data['messages'][-1]] if session_data['messages'] else [],
            'full_log': session_data['messages']
        }, f, indent=2)
    
    return filename.name

def load_session(username, filename):
    """Load a specific session by filename"""
    user_dir = CHAT_HISTORY_DIR / username
    file_path = user_dir / filename
    
    try:
        with open(file_path) as f:
            data = json.load(f)
            if not all(key in data for key in ['metadata', 'full_log']):
                raise ValueError("Invalid session format")
            
            return {
                'filename': file_path.name,
                'timestamp': data['metadata']['created_at'],
                'philosopher': data['metadata']['philosopher'],
                'summary': data['metadata']['summary'],
                'messages': data['full_log'],
                'username': data['metadata']['username']
            }
    except Exception as e:
        raise ValueError(f"Error loading session {file_path}: {e}")