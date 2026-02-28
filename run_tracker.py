import subprocess
import sys
import os

print("Starting SimpleQA Pure File-System Tracker...")
print("The application will be available at http://localhost:8505 (or another free port)")

# Set env var if needed
os.environ["STREAMLIT_SERVER_PORT"] = "8505"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

try:
    subprocess.run(["streamlit", "run", "tracker_app.py"], check=True)
except KeyboardInterrupt:
    print("\nShutting down Tracker...")
except subprocess.CalledProcessError as e:
    print(f"\nError running Streamlit: {e}")
except FileNotFoundError:
    print("\nError: 'streamlit' command not found. Please ensure it is installed and in your PATH.")
    print("You can install it using: pip install streamlit")
    sys.exit(1)
