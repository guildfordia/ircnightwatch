import socket
import re
import requests
import sys
import signal
import os

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


def connect_to_irc():
    """Connect to the IRC server and listen for messages"""
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[DEBUG] Trying to connect to IRC at {SERVER}:{PORT}")
    irc.connect((SERVER, PORT))
    print("[DEBUG] Connected successfully")
    irc.send(f"NICK {NICKNAME}\r\n".encode("utf-8"))
    irc.send(f"USER {NICKNAME} @ * :Sentiment Analysis Bot\r\n".encode("utf-8"))
    irc.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))

    joined = False

    while True:
        try:
            msg = irc.recv(2048).decode("utf-8", errors="ignore").strip()

            if msg:
                print(f"[IRC] {msg}")

            if msg.startswith("PING"):
                irc.send(f"PONG {msg.split()[1]}\r\n".encode("utf-8"))

            if not joined and re.search(r" 001 ", msg):
                print(f"[DEBUG] Sending JOIN to { CHANNEL }")
                irc.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))
                joined = True

            match = re.search(r":(\S+)!.* PRIVMSG (\S+) :(.*)", msg)
            if match:
                user, channel, message = match.groups()
                print(f"{user} in {channel}: {message}")

                # Send message to Sentiment API
                payload = {"user": user, "message": message}
                requests.post(API_URL, json=payload, timeout=5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            break

    irc.close()

def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    connect_to_irc()
