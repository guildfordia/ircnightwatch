from flask import Flask, request, jsonify
from transformers import pipeline
from deep_translator import GoogleTranslator

emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=3
)
app = Flask(__name__)

def translate_to_english(text):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        print(f"[WARN] Translation failed: {e}")
        return text

@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user = data.get("user")
    message = data.get("message")

    message_en = translate_to_english(message)

    result = emotion_model(message_en)
    top_emotions = result[0]
    primary_emotion = top_emotions[0]['label']
    primary_score = top_emotions[0]['score']

    # Pick the most likely emotion
    primary_emotion = top_emotions[0]['label']
    primary_score = top_emotions[0]['score']

    print("=" * 40)
    print(f"Received message:\n  User: {user}\n  Message (orig): {message}")
    print(f"  → Translated: {message_en}")
    for e in result[0]:
        print(f"  → {e['label']}: {e['score']:.2f}")
    print("=" * 40)

    return jsonify({
            "user": user,
            "message": message,
            "primary_emotion": primary_emotion,
            "top_emotions": top_emotions
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
