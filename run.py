# === System Imports ===
import sys
import time
import socket
import subprocess
from pathlib import Path

# === Configuration ===
FLASK_HOST = "127.0.0.1"
FLASK_PORT =  8000 

# Add the current directory to local imports
sys.path.insert(0, str(Path(__file__).parent))

# === Utils ===
def is_port_open(host=FLASK_HOST, port=FLASK_PORT):
    """Check if a TCP port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def run_flask():
    """Launch the Flask redirect server as a subprocess"""
    proc = subprocess.Popen(
        [sys.executable, "server/redirect_server.py"],
        stdout=sys.stdout,  
        stderr=sys.stderr
    )
    return proc

# === Main Execution ===
if __name__ == "__main__":
    print("🚀 Starting Flask redirect server...")
    flask_proc = run_flask()

    # Wait until Flask has fully started
    for i in range(20):  #Ensure Flask starts within 10 seconds.
        if is_port_open():
            print(f"Flask server is running on http://{FLASK_HOST}:{FLASK_PORT}")
            break
        time.sleep(0.5)
    else:
        print("Flask server did not start. Check console logs for errors.")
        flask_proc.terminate()
        sys.exit(1)

    try:
        print("🎨 Starting PyQt5 application...")
        from frontend.main import main
        main()  # Launch the PyQt application
    except Exception as e:
        print(f"Error while running PyQt app: {str(e)}")
    finally:
        print("Stopping Flask server...")
        flask_proc.terminate()
        flask_proc.wait()
        print("Flask server terminated.")
