from flask import Flask, request, jsonify
from transformers import pipeline
from deep_translator import GoogleTranslator
import datetime

ft_save_directory = "./fr_eng_save_pretrained"
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

    emo_result = emotion_model(message_en)
    sent_result = sentiment_model(message_en)

    top_emotions = emo_result[0]
    top_sentiment = sent_result[0]

    # Pick the most likely emotion
    # primary_emotion = top_emotions[0]['label']
    primary_score = top_emotions[0]['score']

    primary_sentiment = top_sentiment[0]['score']

    print("=" * 40)
    print(f"User       : {user}")
    print(f"Message    : {message}")
    print(f"Translated : {message_en}")
    print("\nEmotion results:")
    for e in top_emotions:
        print(f"  - {e['label']}: {e['score']:.2f}")
    print(f"Selected emotion score: {primary_score:.2f}")

    print("\nSentiment results:")
    for s in top_sentiment:
        print(f"  - {s['label']}: {s['score']:.2f}")
    print(f"Selected sentiment score: {primary_sentiment:.2f}")
    print("=" * 40)

    return jsonify({
        "id": datetime.datetime.now(),
        "values":{
            'sentiment': {
                'probas': sent_result,
                'output': primary_sentiment,
            },
            'emotion': {
                'probas': emo_result,
                'output': primary_score
            }
        }
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
