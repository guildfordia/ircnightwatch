import socket
import re
import requests
import sys
import signal
import os
import time

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
API_URL = os.getenv("API_URL", f"http://{SERVER}:5000/receive")

running = True
attempts = 0

def connect_to_irc():
    global running
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

            while running:
                msg = irc.recv(2048).decode("utf-8", errors="ignore").strip()

                joined = False

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
                    # irc.send(f"PONG {msg.split()[1]}\r\n".encode("utf-8"))
                    token = msg.split(":", 1)[1] if ":" in msg else ""
                    pong_msg = f"PONG :{token}\r\n"
                    print(f"[PING] -> {pong_msg.strip()}")
                    irc.send(pong_msg.encode("utf-8"))

                match = re.search(r":(\S+)!.* PRIVMSG (\S+) :(.*)", msg)
                if match:
                    user, channel, message = match.groups()
                    print(f"{user} in {channel}: {message}")

                    # Send message to Sentiment API
                    payload = {"user": user, "message": message}
                    try:
                        requests.post(API_URL, json=payload, timeout=5)
                    except Exception as e:
                        print(f"[WARN] Failed to send to API: {e}")

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

def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    connect_to_irc()
