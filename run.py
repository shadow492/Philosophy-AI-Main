import os
import subprocess
import time
import requests
from requests.exceptions import ConnectionError
import sys
import logging
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for process management
django_process = None
streamlit_process = None

def setup_django_database():
    """Set up Django database"""
    try:
        logger.info("Setting up Django database...")
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set up Django database: {e}")
        return False

def run_django():
    """Run the Django backend server as a subprocess"""
    logger.info("Starting Django backend server...")
    
    # Set environment variable for Django settings
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'philosophy_project.settings'
    
    # Start Django server as a subprocess
    cmd = [sys.executable, 'manage.py', 'runserver', '8000']
    
    try:
        # Use subprocess.Popen to start the server
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start a thread to read and log the output
        def log_output(process):
            for line in iter(process.stdout.readline, ''):
                logger.info(f"Django: {line.strip()}")
        
        import threading
        log_thread = threading.Thread(target=log_output, args=(process,))
        log_thread.daemon = True
        log_thread.start()
        
        logger.info(f"Django server started with PID: {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start Django server: {e}")
        return None

def run_streamlit():
    """Run the Streamlit frontend as a subprocess"""
    logger.info("Starting Streamlit frontend...")
    
    # Set environment variables for Streamlit
    env = os.environ.copy()
    
    # Start Streamlit as a subprocess
    cmd = [sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py']
    
    try:
        # Use subprocess.Popen to start Streamlit
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start a thread to read and log the output
        def log_output(process):
            for line in iter(process.stdout.readline, ''):
                logger.info(f"Streamlit: {line.strip()}")
        
        import threading
        log_thread = threading.Thread(target=log_output, args=(process,))
        log_thread.daemon = True
        log_thread.start()
        
        global streamlit_process
        streamlit_process = process
        
        logger.info(f"Streamlit started with PID: {process.pid}")
        
        # Wait for Streamlit to start
        time.sleep(2)
        
        # Open browser
        import webbrowser
        webbrowser.open('http://localhost:8501')
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Failed to start Streamlit: {e}")
        return None

def cleanup(signum=None, frame=None):
    """Clean up resources before exiting"""
    logger.info("Cleaning up resources...")
    
    # Terminate Django process
    global django_process
    if django_process:
        logger.info(f"Terminating Django process (PID: {django_process.pid})...")
        django_process.terminate()
        django_process.wait()
        django_process = None
    
    # Terminate Streamlit process
    global streamlit_process
    if streamlit_process:
        logger.info(f"Terminating Streamlit process (PID: {streamlit_process.pid})...")
        streamlit_process.terminate()
        streamlit_process.wait()
        streamlit_process = None
    
    logger.info("Cleanup complete")
    
    # Exit if called as signal handler
    if signum:
        sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Check if port 8000 is already in use
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    if result == 0:
        logger.error("Port 8000 is already in use. Please stop any running Django servers first.")
        sys.exit(1)
    sock.close()
    
    # Set up Django database
    if not setup_django_database():
        logger.error("Failed to set up Django database. Exiting.")
        sys.exit(1)
    
    # Start Django as a subprocess
    django_process = run_django()
    if not django_process:
        logger.error("Failed to start Django server. Exiting.")
        sys.exit(1)
    
    # Wait for Django to start
    logger.info("Waiting for Django server to start...")
    for i in range(10):
        try:
            response = requests.get('http://localhost:8000/api/ping/')
            if response.status_code == 200:
                logger.info("Django server is ready")
                break
        except ConnectionError:
            logger.info(f"Waiting for Django server... ({i+1}/10)")
            time.sleep(1)
    else:
        logger.error("Django server failed to start in time. Exiting.")
        cleanup()
        sys.exit(1)
    
    try:
        # Run Streamlit in the main thread
        run_streamlit()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        # Clean up resources
        cleanup()