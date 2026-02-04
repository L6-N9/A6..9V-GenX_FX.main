#!/usr/bin/env python3
"""
Simple GenX FX API Server
Uses built-in HTTP server for maximum compatibility
"""

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Add the api directory to Python path
sys.path.append(str(Path(__file__).parent / "api"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api-server.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class GenXAPIHandler(BaseHTTPRequestHandler):
    """
    An HTTP request handler for the GenX FX API, responsible for routing
    and handling GET and POST requests.
    """

    def do_GET(self):
        """
        Handles GET requests for various endpoints, including health checks,
        predictions, signals, and documentation.
        """
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == "/" or path == "/health":
                self.send_health_response()
            elif path == "/api/v1/predictions":
                self.send_predictions_response()
            elif path == "/api/v1/signals":
                self.send_signals_response()
            elif path == "/docs":
                self.send_docs_response()
            else:
                self.send_error(404, "Not Found")

        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, "Internal Server Error")

    def do_POST(self):
        """
        Handles POST requests for submitting signals.
        """
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == "/api/v1/predictions" or path == "/api/signals":
                self.handle_signal_post()
            else:
                self.send_error(404, "Not Found")

        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, "Internal Server Error")

    def send_health_response(self):
        """
        Sends a JSON response for the health check endpoint.
        """
        response = {
            "message": "GenX-FX Trading Platform API",
            "version": "1.0.0",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "github": "Mouy-leng",
            "repository": "https://github.com/Mouy-leng/GenX_FX.git",
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def send_predictions_response(self):
        """
        Sends a JSON response for the predictions endpoint.
        """
        response = {
            "predictions": [],
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def send_signals_response(self):
        """
        Sends a JSON response containing signals read from a CSV file.
        """
        # Read signals from CSV file if it exists
        signals = []
        if os.path.exists("MT4_Signals.csv"):
            try:
                with open("MT4_Signals.csv", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # Skip header
                        for line in lines[1:]:
                            parts = line.strip().split(",")
                            if len(parts) >= 8:
                                signals.append(
                                    {
                                        "timestamp": parts[0],
                                        "symbol": parts[1],
                                        "action": parts[2],
                                        "entry_price": float(parts[3]),
                                        "stop_loss": float(parts[4]),
                                        "take_profit": float(parts[5]),
                                        "confidence": float(parts[6]),
                                        "reasoning": parts[7],
                                        "source": (
                                            parts[8] if len(parts) > 8 else "unknown"
                                        ),
                                    }
                                )
            except Exception as e:
                logger.error(f"Error reading signals: {e}")

        response = {
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat(),
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def send_docs_response(self):
        """
        Sends an HTML response with API documentation.
        """
        docs = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GenX FX API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .method { color: #007acc; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>GenX FX Trading Platform API</h1>
            <p>Version: 1.0.0</p>
            
            <h2>Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> /health
                <p>Health check endpoint</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> /api/v1/predictions
                <p>Get trading predictions</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> /api/v1/signals
                <p>Get trading signals</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> /api/v1/predictions
                <p>Submit trading signals</p>
            </div>
            
            <h2>Usage</h2>
            <p>Base URL: http://localhost:8080</p>
            <p>All responses are in JSON format</p>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(docs.encode())

    def handle_signal_post(self):
        """
        Handles the submission of trading signals via a POST request.
        """
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            # Log the received signals
            if "signals" in data:
                logger.info(f"Received {len(data['signals'])} signals")
                for signal in data["signals"]:
                    logger.info(
                        f"Signal: {signal.get('symbol', 'Unknown')} {signal.get('action', 'Unknown')}"
                    )

            response = {
                "message": "Signals received successfully",
                "count": len(data.get("signals", [])),
                "timestamp": datetime.now().isoformat(),
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            logger.error(f"Error handling signal POST: {e}")
            self.send_error(400, "Bad Request")

    def log_message(self, format, *args):
        """
        Overrides the default log_message to use the application's logger.
        """
        logger.info(f"{self.address_string()} - {format % args}")


class GenXAPIServer:
    """
    A class to manage the GenX FX API server.
    """

    def __init__(self, host="0.0.0.0", port=8080):
        """
        Initializes the API server.

        Args:
            host (str, optional): The host to bind the server to. Defaults to "0.0.0.0".
            port (int, optional): The port to run the server on. Defaults to 8080.
        """
        self.host = host
        self.port = port
        self.server = None
        self.running = False

    def start(self) -> bool:
        """
        Starts the API server in a separate thread.

        Returns:
            bool: True if the server starts successfully, False otherwise.
        """
        try:
            self.server = HTTPServer((self.host, self.port), GenXAPIHandler)
            self.running = True

            logger.info(f"GenX FX API Server started on {self.host}:{self.port}")
            logger.info(f"API Documentation: http://{self.host}:{self.port}/docs")
            logger.info(f"Health Check: http://{self.host}:{self.port}/health")
            logger.info(f"Signals: http://{self.host}:{self.port}/api/v1/signals")

            # Start server in a separate thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            return True

        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return False

    def stop(self):
        """
        Stops the API server.
        """
        if self.server:
            self.server.shutdown()
            self.running = False
            logger.info("API server stopped")


def main():
    """
    The main entry point for the simple API server.
    """
    logger.info("Starting GenX FX Simple API Server...")

    # Create API server
    api_server = GenXAPIServer()

    if api_server.start():
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down API server...")
        finally:
            api_server.stop()
    else:
        logger.error("Failed to start API server")
        sys.exit(1)


if __name__ == "__main__":
    main()
