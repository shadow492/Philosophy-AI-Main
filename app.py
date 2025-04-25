# Add this at the top with other imports
import uuid
from datetime import datetime
import streamlit as st
import os
import time
from dotenv import load_dotenv

# Configure Streamlit page - MUST be the first Streamlit command
st.set_page_config(
    page_title="Philosophical Dialogues",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Import our modules - removing chat_history and session_management imports
from philosophers import PHILOSOPHERS, get_philosopher, get_all_philosophers
from groq_client import GroqClient

# Load environment variables
load_dotenv()

# Simplified functions without session saving
def get_philosopher_response(user_input):
    """Get response from the philosopher"""
    philosopher = PHILOSOPHERS[st.session_state.current_philosopher]
    
    # Create a properly ordered message list
    messages = []
    
    # First add system message
    messages.append({'role': 'system', 'content': philosopher['system_message']})
    
    # Add conversation history
    history = st.session_state.messages.copy()
    
    # Add all previous messages
    for msg in history:
        messages.append(msg)
    
    # Create a new Groq client instance
    groq_client = GroqClient()
    
    # Get response from Groq
    try:
        response = groq_client.generate_response(messages)
        return response
    except Exception as e:
        print(f"Error getting response: {e}")
        return "I apologize, but I need a moment to gather my thoughts. Please try your question again."

def summarize_conversation(messages):
    """Generate a summary of the conversation"""
    if not messages or len(messages) < 2:
        return "New conversation"
    
    try:
        groq_client = GroqClient()
        return groq_client.summarize_conversation(messages)
    except Exception as e:
        print(f"Error summarizing conversation: {e}")
        return "Philosophical dialogue"

def create_new_chat():
    """Create a new chat session"""
    # Generate a new chat ID for the session state
    chat_id = f"chat_{uuid.uuid4().hex[:8]}_{int(time.time())}"
    
    # If chats dictionary doesn't exist, create it
    if 'chats' not in st.session_state:
        st.session_state.chats = {}
    
    # Save current chat if it exists
    if 'current_chat_id' in st.session_state and st.session_state.messages:
        current_id = st.session_state.current_chat_id
        st.session_state.chats[current_id] = {
            'messages': st.session_state.messages.copy(),
            'philosopher': st.session_state.current_philosopher,
            'timestamp': datetime.now().isoformat(),
            'summary': summarize_conversation(st.session_state.messages)
        }
    
    # Create new empty chat
    st.session_state.messages = []
    st.session_state.current_chat_id = chat_id
    st.session_state.summary = "New conversation"
    
    # Make sure the new chat is saved in the chats dictionary
    st.session_state.chats[chat_id] = {
        'messages': [],
        'philosopher': st.session_state.current_philosopher,
        'timestamp': datetime.now().isoformat(),
        'summary': "New conversation"
    }

def switch_chat(chat_id):
    """Switch to a different chat"""
    # Don't do anything if we're already on this chat
    if chat_id == st.session_state.current_chat_id:
        return
    
    # Make sure the chat exists
    if chat_id not in st.session_state.chats:
        st.error(f"Chat {chat_id} not found")
        return
        
    # Save current chat
    if st.session_state.messages:
        current_id = st.session_state.current_chat_id
        st.session_state.chats[current_id] = {
            'messages': st.session_state.messages.copy(),
            'philosopher': st.session_state.current_philosopher,
            'timestamp': datetime.now().isoformat(),
            'summary': summarize_conversation(st.session_state.messages)
        }
    
    # Load selected chat
    chat_data = st.session_state.chats[chat_id]
    st.session_state.messages = chat_data['messages'].copy()  # Use copy to avoid reference issues
    st.session_state.current_philosopher = chat_data['philosopher']
    st.session_state.current_chat_id = chat_id
    
    # Force a rerun to update the UI
    st.rerun()

def delete_chat(chat_id):
    """Delete a chat from session state"""
    if chat_id in st.session_state.chats:
        # Check if we're deleting the current chat
        is_current = st.session_state.current_chat_id == chat_id
        
        # Delete the chat
        del st.session_state.chats[chat_id]
        
        # If we deleted the current chat and there are other chats, switch to another one
        if is_current:
            if st.session_state.chats:
                # Get the newest chat ID based on timestamp
                other_chats = list(st.session_state.chats.items())
                other_chats.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                new_chat_id = other_chats[0][0]
                
                # Load that chat
                chat_data = st.session_state.chats[new_chat_id]
                st.session_state.messages = chat_data['messages'].copy()
                st.session_state.current_philosopher = chat_data['philosopher']
                st.session_state.current_chat_id = new_chat_id
            else:
                # If no chats left, create a new empty one
                create_new_chat()

def switch_philosopher(philosopher_id):
    """Switch the current philosopher"""
    if philosopher_id != st.session_state.current_philosopher:
        st.session_state.current_philosopher = philosopher_id
        # Add a system message indicating the philosopher change
        philosopher = PHILOSOPHERS[philosopher_id]
        st.session_state.messages.append({
            'role': 'system', 
            'content': f"*The conversation continues with {philosopher['name']}*"
        })

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_philosopher' not in st.session_state:
    st.session_state.current_philosopher = 'marcus_aurelius'
if 'chats' not in st.session_state:
    st.session_state.chats = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = f"chat_{uuid.uuid4().hex[:8]}_{int(time.time())}"
if 'summary' not in st.session_state:
    st.session_state.summary = "New conversation"

# Sidebar for chat history only
with st.sidebar:
    st.title("Chat History")
    
    # Add New Chat button to sidebar
    if st.button("New Chat", key="new_chat_sidebar"):
        create_new_chat()
    
    st.divider()  # Add a divider between the button and chat history
    
    # Display current chat first
    
    
    # Display other chats in reverse chronological order (newest first)
    other_chats = [(chat_id, chat_data) for chat_id, chat_data in st.session_state.chats.items() 
                  if chat_id != st.session_state.current_chat_id]
    
    # Sort by timestamp (newest first)
    other_chats.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
    
    if other_chats:
        for chat_id, chat_data in other_chats:
            # Create a button for each chat with the summary as the label
            summary = chat_data.get('summary', 'Untitled conversation')
            if summary and len(summary) > 30:
                summary = summary[:27] + "..."
            
            # Show philosopher icon and summary
            philosopher_data = PHILOSOPHERS.get(chat_data['philosopher'], PHILOSOPHERS['marcus_aurelius'])
            label = f"{philosopher_data['avatar']} {summary}"
            
            # Use a container to ensure consistent UI
            with st.container():
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    if st.button(label, key=f"session_{chat_id}"):
                        switch_chat(chat_id)
                with col2:
                    if st.button("🗑️", key=f"delete_{chat_id}"):
                        delete_chat(chat_id)
                        st.rerun()  # Force rerun after deletion
    elif not st.session_state.chats:
        st.info("No other chats in this session")

# Main chat interface
st.title("Philosophical Dialogues")

# Add philosopher dropdown in a single row
# Create a dropdown for philosopher selection
philosopher_options = [(id, f"{data['avatar']} {data['name']}") for id, data in PHILOSOPHERS.items()]
philosopher_dict = {name: id for id, name in philosopher_options}

selected_philosopher = st.selectbox(
    "Choose Your Philosopher",
    options=[name for _, name in philosopher_options],
    index=list(PHILOSOPHERS.keys()).index(st.session_state.current_philosopher)
)

# Handle philosopher change
selected_id = philosopher_dict[selected_philosopher]
if selected_id != st.session_state.current_philosopher:
    switch_philosopher(selected_id)

# Display current philosopher information
current_philosopher = PHILOSOPHERS[st.session_state.current_philosopher]
st.subheader(f"Dialogue with {current_philosopher['name']}")

# Remove the New Chat button from here

# Display title if it exists in the philosopher data
if 'title' in current_philosopher:
    st.caption(current_philosopher['title'])

# Display chat messages
for message in st.session_state.messages:
    role = message['role']
    content = message['content']
    
    if role == 'user':
        with st.chat_message("user", avatar="👤"):
            st.write(content)
    elif role == 'system':
        # Display system messages (like philosopher changes) as info messages
        st.info(content)
    else:
        with st.chat_message("assistant", avatar=current_philosopher['avatar']):
            st.write(content)

# Chat input
if prompt := st.chat_input('What philosophical question would you like to explore?'):
    # Add user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    
    # Force a rerun to display the user message immediately
    st.rerun()

# Check if we need to generate a response (when the last message is from the user)
if st.session_state.messages and st.session_state.messages[-1]['role'] == 'user':
    with st.spinner(f"{current_philosopher['name']} is contemplating..."):
        # Get the last user message
        last_user_message = st.session_state.messages[-1]['content']
        
        # Generate response
        response = get_philosopher_response(last_user_message)
        
        # Add assistant response to chat history
        st.session_state.messages.append({'role': 'assistant', 'content': response})
        
        # Update the current chat in the chats dictionary
        st.session_state.chats[st.session_state.current_chat_id] = {
            'messages': st.session_state.messages.copy(),
            'philosopher': st.session_state.current_philosopher,
            'timestamp': datetime.now().isoformat(),
            'summary': summarize_conversation(st.session_state.messages)
        }
        
        # Force a rerun to display the assistant message
        st.rerun()
