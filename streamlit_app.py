import streamlit as st
import requests
import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Philosophical Dialogues",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# API URL
API_URL = "http://localhost:8000/api"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user' not in st.session_state:
    st.session_state.user = None

# Authentication functions
def register_user(username, email, password, password2):
    try:
        # Log the data being sent
        logger.info(f"Sending registration data: username={username}, email={email}")
        
        # Create the request payload
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "password2": password2
        }
        
        # Make the request
        response = requests.post(
            f"{API_URL}/auth/register/",
            json=payload
        )
        
        # Log the response
        logger.info(f"Registration response status: {response.status_code}")
        
        # If there's an error, log the response content
        if response.status_code != 201:
            logger.error(f"Registration error: {response.text}")
            return False, response.text
        
        # Process successful response
        data = response.json()
        st.session_state.auth_token = data.get('access')
        st.session_state.user = data.get('user')
        return True, "Registration successful!"
    except Exception as e:
        logger.error(f"Registration exception: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('detail', str(e))
                return False, error_message
            except:
                return False, str(e)
        return False, str(e)

def login_user(username, password):
    try:
        # Log the login attempt
        logger.info(f"Attempting login for user: {username}")
        
        # Make the request
        response = requests.post(
            f"{API_URL}/auth/login/",
            json={"username": username, "password": password}
        )
        
        # Log the response
        logger.info(f"Login response status: {response.status_code}")
        logger.info(f"Login response: {response.text}")
        
        # If there's an error, log the response content
        if response.status_code != 200:
            logger.error(f"Login error: {response.text}")
            return False, response.text
        
        # Process successful response
        data = response.json()
        st.session_state.auth_token = data.get('access')
        st.session_state.user = data.get('user')
        return True, "Login successful!"
    except Exception as e:
        logger.error(f"Login exception: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('detail', str(e))
                return False, error_message
            except:
                return False, str(e)
        return False, str(e)

def logout_user():
    st.session_state.auth_token = None
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.current_chat_id = None
    st.rerun()

# Authentication UI
def show_auth_ui():
    st.title("Philosophical Dialogues")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, message = login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with tab2:
        st.header("Register")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        password2 = st.text_input("Confirm Password", type="password", key="register_password2")
        
        if st.button("Register"):
            if not username or not email or not password or not password2:
                st.error("Please fill in all fields")
            elif password != password2:
                st.error("Passwords do not match")
            else:
                success, message = register_user(username, email, password, password2)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

# Main app
def main():
    # Add a debug section at the top
    with st.expander("Debug Info"):
        st.write("API URL:", API_URL)
        st.write("Auth Token:", st.session_state.auth_token[:10] + "..." if st.session_state.auth_token else "None")
        st.write("User:", st.session_state.user)
        if st.button("Test API Connection"):
            try:
                response = requests.get(f"{API_URL}/ping/")
                st.write(f"API Status: {response.status_code}")
                st.write(f"Response: {response.json()}")
            except Exception as e:
                st.error(f"API Connection Error: {str(e)}")
    
    if st.session_state.auth_token is None:
        show_auth_ui()
    else:
        # Add logout button to sidebar
        with st.sidebar:
            st.write(f"Logged in as: {st.session_state.user['username']}")
            if st.button("Logout"):
                logout_user()
        
        # Main chat interface
        st.title("Philosophical Dialogues")
        
        # Fix the sidebar chat listing section
        with st.sidebar:
            st.header("Chat Sessions")
            
            # Get available philosophers
            try:
                # Add authentication headers to the philosophers request
                headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if st.session_state.auth_token else {}
                response = requests.get(f"{API_URL}/philosophers/", headers=headers)
                philosophers = response.json()
                
                # Check if philosophers is empty or not a list
                if not philosophers or not isinstance(philosophers, list):
                    st.warning("No philosophers available")
                    philosophers = [{"id": "marcus_aurelius", "name": "Marcus Aurelius"}]  # Default fallback
            except Exception as e:
                st.error(f"Error loading philosophers: {str(e)}")
                philosophers = [{"id": "marcus_aurelius", "name": "Marcus Aurelius"}]  # Default fallback
            
            # Create new chat button
            selected_philosopher = st.selectbox(
                "Choose a philosopher",
                options=[p["id"] for p in philosophers],
                format_func=lambda x: next((p["name"] for p in philosophers if p["id"] == x), x)
            )
            
            if st.button("New Chat"):
                try:
                    # Ensure we have a token
                    if not st.session_state.auth_token:
                        st.error("You must be logged in to create a chat")
                    else:
                        # Set up headers with the token
                        headers = {
                            "Authorization": f"Bearer {st.session_state.auth_token}",
                            "Content-Type": "application/json"
                        }
                        
                        # Make the request
                        response = requests.post(
                            f"{API_URL}/sessions/create_session/",
                            json={"philosopher": selected_philosopher},
                            headers=headers
                        )
                        
                        # Check if the response is successful
                        if response.status_code >= 400:
                            st.error(f"Error creating chat: {response.text}")
                        else:
                            # Parse the response
                            session = response.json()
                            
                            # Set the current chat ID
                            st.session_state.current_chat_id = session.get("id")
                            st.session_state.messages = []
                            st.rerun()
                except Exception as e:
                    st.error(f"Error creating chat: {str(e)}")
            
            # List existing chats - MOVED OUTSIDE THE NEW CHAT BUTTON BLOCK
            st.subheader("Your Chats")
            try:
                # Add authentication headers to the sessions request
                headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if st.session_state.auth_token else {}
                
                # Make the request
                response = requests.get(
                    f"{API_URL}/sessions/",
                    headers=headers
                )
                
                # Check if the response is successful
                if response.status_code >= 400:
                    st.error(f"Error loading chats: {response.text}")
                else:
                    # Parse the response
                    sessions = response.json()
                    
                    # Reverse the sessions to show newest first
                    sessions = sorted(sessions, key=lambda x: x.get('updated_at', ''), reverse=True)
                    
                    # Display the sessions
                    for session in sessions:
                        # Handle case where summary might be None
                        summary = session.get('summary', 'New conversation')
                        summary_text = summary[:20] + "..." if summary and len(summary) > 20 else summary or "New conversation"
                        
                        if st.button(f"{session['philosopher']} - {summary_text}", key=session["id"]):
                            st.session_state.current_chat_id = session["id"]
                            # Load messages
                            st.session_state.messages = [
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in session.get("messages", [])
                            ]
                            st.rerun()
            except Exception as e:
                st.error(f"Error loading chats: {str(e)}")
        
        # Chat interface
        if st.session_state.current_chat_id:
            # Add philosopher switcher to the sidebar when a chat is active
            with st.sidebar:
                st.divider()
                st.subheader("Current Chat Settings")
                
                # Get current philosopher from API
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                    response = requests.get(
                        f"{API_URL}/sessions/{st.session_state.current_chat_id}/",
                        headers=headers
                    )
                    current_session = response.json()
                    current_philosopher_id = current_session.get('philosopher', 'marcus_aurelius')
                    
                    # Philosopher switcher
                    new_philosopher = st.selectbox(
                        "Change Philosopher",
                        options=[p["id"] for p in philosophers],
                        index=[i for i, p in enumerate(philosophers) if p["id"] == current_philosopher_id][0] 
                            if current_philosopher_id in [p["id"] for p in philosophers] else 0,
                        format_func=lambda x: next((p["name"] for p in philosophers if p["id"] == x), x),
                        key="philosopher_switcher"
                    )
                    
                    if new_philosopher != current_philosopher_id and st.button("Switch Philosopher"):
                        try:
                            response = requests.patch(
                                f"{API_URL}/sessions/{st.session_state.current_chat_id}/change-philosopher/",
                                json={"philosopher": new_philosopher},
                                headers=headers
                            )
                            
                            if response.status_code == 200:
                                st.success("Philosopher changed successfully!")
                                # Reload messages after change
                                response = requests.get(
                                    f"{API_URL}/sessions/{st.session_state.current_chat_id}/",
                                    headers=headers
                                )
                                updated_session = response.json()
                                st.session_state.messages = [
                                    {"role": msg["role"], "content": msg["content"]}
                                    for msg in updated_session.get("messages", [])
                                ]
                                st.rerun()
                            else:
                                st.error(f"Failed to change philosopher: {response.text}")
                        except Exception as e:
                            st.error(f"Error changing philosopher: {str(e)}")
                except Exception as e:
                    st.error(f"Error getting session details: {str(e)}")

            # Display chat messages
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                elif message["role"] == "assistant":
                    st.chat_message("assistant").write(message["content"])
            
            # Input for new message
            if prompt := st.chat_input("What would you like to discuss?"):
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                
                # Get AI response
                with st.spinner("Thinking..."):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if st.session_state.auth_token else {}
                        response = requests.post(
                            f"{API_URL}/sessions/{st.session_state.current_chat_id}/add_message/",
                            json={"message": prompt},
                            headers=headers
                        )
                        ai_response = response.json().get("response", "I apologize, but I'm having trouble responding right now.")
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                        st.chat_message("assistant").write(ai_response)
                    except Exception as e:
                        st.error(f"Error getting response: {str(e)}")
        else:
            st.info("Select a chat from the sidebar or create a new one.")
            
            if st.session_state.current_chat_id:
                st.divider()
                st.subheader("Current Chat Settings")
                
                # Get current philosopher
                current_philosopher = next(
                    (p for p in philosophers if p["id"] == selected_philosopher),
                    {"id": "marcus_aurelius", "name": "Marcus Aurelius"}
                )
                
                # Philosopher switcher
                new_philosopher = st.selectbox(
                    "Change Philosopher",
                    options=[p["id"] for p in philosophers],
                    index=[p["id"] for p in philosophers].index(current_philosopher["id"]),
                    format_func=lambda x: next((p["name"] for p in philosophers if p["id"] == x), x),
                    key="philosopher_switcher"
                )
                
                if st.button("Switch Philosopher"):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                        response = requests.patch(
                            f"{API_URL}/sessions/{st.session_state.current_chat_id}/change_philosopher/",
                            json={"philosopher": new_philosopher},
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            st.success("Philosopher changed successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to change philosopher: {response.text}")
                    except Exception as e:
                        st.error(f"Error changing philosopher: {str(e)}")

if __name__ == "__main__":
    main()