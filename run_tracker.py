import os
import subprocess
import sys


def run_app():
    print("Starting SimpleQA Pure File-System Tracker...")
    print("The application will be available at http://localhost:8505 (or another free port)")

    # Set env var if needed
    os.environ["STREAM_LIMIT_SERVER_PORT"] = "8505"
    os.environ["STREAMLIMIT_BROWSER_GATHER_USAGE_STATS"] = "false"

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


if __name__ == "__main__":  # pragma: no cover
    run_app()
