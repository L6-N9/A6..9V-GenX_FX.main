import subprocess
import time
import webbrowser
from threading import Thread


def start_backend():
    """
    Starts the backend server using the main.py script in the api directory.
    """
    subprocess.run(["python", "api/main.py"], cwd="D:/GenX_FX")


def start_frontend():
    """
    Starts the frontend server using 'npx serve' on the 'dist' directory.
    """
    subprocess.run(["npx", "serve", "dist", "-p", "3000"], cwd="D:/GenX_FX")


def start_local_servers():
    """
    Starts both the backend and frontend servers in separate threads for local development.
    """
    print("🚀 Starting GenX-FX Local Servers...")

    # Start backend in thread
    backend_thread = Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()

    time.sleep(2)

    # Start frontend in thread
    frontend_thread = Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()

    time.sleep(3)

    print("✅ GenX-FX is running locally:")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8080")
    print("📊 API Docs: http://localhost:8080/docs")

    # Open browser
    webbrowser.open("http://localhost:3000")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")


if __name__ == "__main__":
    start_local_servers()
