import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from transformers import pipeline
from deep_translator import GoogleTranslator
import datetime
import socket
import json
import requests

emotion_model = pipeline(
     "text-classification",
     model="j-hartmann/emotion-english-distilroberta-base",
     top_k=3
)
sentiment_model = pipeline(
    "text-classification",
    model="finiteautomata/bertweet-base-sentiment-analysis",
    top_k=3
)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

#MAX_HOST="host.docker.internal"
#MAX_PORT=5050

latest_results = {}

#def send_to_max(data):
#    try:
#        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        message = json.dumps(data)
#        sock.sendto(message.encode(), (MAX_HOST, MAX_PORT))
#    except Exception as e:
#        print(f"[ERROR] Failed to send to Max: {e}")

def translate_to_english(text):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        print(f"[WARN] Translation failed: {e}")
        return text

@app.route('/receive', methods=['POST'])
def receive():
    global latest_results
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user = data.get("user")
    message = data.get("message")

    translated = translate_to_english(message)

    print("=" * 40)
    print(f"User       : {user}")
    print(f"Message    : {message}")
    print(f"Translated : {translated}")

    emo_result = emotion_model(translated)[0]
    sent_result = sentiment_model(translated)[0]

    print("\nEmotion results:")
    for e in emo_result:
        print(f"  - {e['label']}: {e['score']:.2f}")
    print("\nSentiment results:")
    for s in sent_result:
        print(f"  - {s['label']}: {s['score']:.2f}")

    # Pick the most likely emotion
    # primary_emotion = top_emotions[0]['label']
    primary_emotion = emo_result[0]['label']
    primary_sentiment = sent_result[0]['label']
    
    print(f"Selected emotion label: {primary_emotion}")
    print(f"Selected sentiment label: {primary_sentiment}")
    print("=" * 40)

    max_data = {
        #"id": int(datetime.datetime.now().timestamp() * 1000),
        'data': {
             'sentiment': {
                'probas': sent_result,
                'output': primary_sentiment,
             },
             'emotion': {
                'probas': emo_result,
                'output': primary_emotion
            }
        }
    }

    latest_results = max_data

    print(json.dumps(max_data, indent=2))

    socketio.emit('sentiment_event', max_data)

    return jsonify(max_data), 201

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000)
    socketio.run(app, host='0.0.0.0', port=5000)
