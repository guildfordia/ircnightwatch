import socket
import re
import requests
import sys
import signal
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def resolve_irc_host():
    """Try to connect to host.docker.internal:6667, fallback to 172.17.0.1"""
    test_hosts = ["ngircd", "172.17.0.1"]
    for host in test_hosts:
        try:
            with socket.create_connection((host, 6667), timeout=2):
                print(f"[INFO] Using IRC host: {host}")
                return host
        except Exception as e:
            print(f"[WARN] Could not connect to {host}:6667 ({e})")
    print("[ERROR] Could not connect to any IRC host.")
    return test_hosts[-1]  # fallback anyway


# IRC Server Config
SERVER = os.getenv("IRC_HOST", resolve_irc_host())
PORT = int(os.getenv("IRC_PORT", 6667))
CHANNEL = os.getenv("IRC_CHANNEL", "#nightwatch")
NICKNAME = os.getenv("IRC_NICKNAME", "SentimentBot")

# JSON API Endpoint
API_HOST = os.getenv("SENTIMENT_API_HOST", "sentiment-api")
API_PORT = os.getenv("SENTIMENT_API_PORT", "6000")
API_URL = os.getenv("API_URL", f"http://{API_HOST}:{API_PORT}/receive")

# Configure retry strategy
retry_strategy = Retry(
    total=5,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
    status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)

running = True

def connect_to_irc():
    global running
    attempts = 0
    while running:
        try:
            print(f"[DEBUG] Connecting to {SERVER}: {PORT}")
            """Connect to the IRC server and listen for messages"""
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[DEBUG] Trying to connect to IRC at {SERVER}:{PORT}")
            irc.connect((SERVER, PORT))
            print("[DEBUG] Connected successfully")
            irc.send(f"NICK {NICKNAME}\r\n".encode("utf-8"))
            irc.send(f"USER {NICKNAME} @ * :Sentiment Analysis Bot\r\n".encode("utf-8"))

            last_ping = time.time()
            joined = False

            while running:
                try:
                    msg = irc.recv(2048).decode("utf-8", errors="ignore").strip()
                    if not msg:
                        print("[WARN] Empty message received, server might be down")
                        break

                    if "Server going down" in msg:
                        print("[INFO] Server is going down, will reconnect...")
                        break

                    if not joined and re.search(r" 001 ", msg):
                        print(f"[DEBUG] Sending JOIN to {CHANNEL}")
                        irc.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))
                        joined = True

                    if time.time() - last_ping > 60:
                        print("⏳ Still connected...")
                        last_ping = time.time()

                    if msg:
                        print(f"[IRC] {msg}")

                    if msg.startswith("PING"):
                        token = msg.split(":", 1)[1] if ":" in msg else ""
                        pong_msg = f"PONG :{token}\r\n"
                        print(f"[PING] -> {pong_msg.strip()}")
                        irc.send(pong_msg.encode("utf-8"))

                    match = re.search(r":(\S+)!.* PRIVMSG (\S+) :(.*)", msg)
                    if match:
                        user, channel, message = match.groups()
                        print(f"{user} in {channel}: {message}")

                        # Send message to Sentiment API with retry mechanism
                        payload = {"user": user, "message": message}
                        try:
                            http.post(API_URL, json=payload, timeout=5)
                        except Exception as e:
                            print(f"[WARN] Failed to send to API after retries: {e}")

                except socket.error as e:
                    print(f"[ERROR] Socket error: {e}")
                    break

        except Exception as e:
            attempts += 1
            print(f"[ERROR] IRC connection #{attempts} failed: {e}")
            time.sleep(5)
        finally:
            try:
                irc.close()
            except:
                pass
            print("[INFO] Attempting to reconnect...")
            time.sleep(5)  # Add delay before reconnection attempt

def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    connect_to_irc()
