import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from deep_translator import GoogleTranslator
import datetime
import socket
import json
import requests
import logging
import os
import sys
import torch
from concurrent.futures import ThreadPoolExecutor
import threading
from pathlib import Path
import time
from functools import wraps
import shutil

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Create persistent cache directory
CACHE_DIR = Path("/root/.cache")

# Ensure cache directory exists and has proper permissions
def setup_cache_directory():
    try:
        # Create cache directory if it doesn't exist
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Set permissions to ensure writability
        os.chmod(CACHE_DIR, 0o777)
        
        logger.info(f"Cache directory set up at {CACHE_DIR}")
    except Exception as e:
        logger.error(f"Failed to set up cache directory: {e}")
        raise

# Set up cache directory on startup
setup_cache_directory()

# Global cache for models
model_cache = {}
model_lock = threading.Lock()

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def load_model(model_name, task="text-classification", top_k=3):
    """Load a model with caching and optimized settings"""
    with model_lock:
        if model_name in model_cache:
            logger.info(f"Using cached model: {model_name}")
            return model_cache[model_name]
        
        logger.info(f"Loading model: {model_name}")
        try:
            # Set timeout for model loading
            os.environ['TRANSFORMERS_OFFLINE'] = '0'
            os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '300'  # 5 minutes timeout
            
            # Configure cache settings
            os.environ['TRANSFORMERS_CACHE'] = str(CACHE_DIR)
            os.environ['HF_HOME'] = str(CACHE_DIR)
            
            # Debug: Check cache directory
            logger.info(f"Cache directory contents before loading: {list(CACHE_DIR.glob('*'))}")
            logger.info(f"Environment variables: TRANSFORMERS_CACHE={os.environ.get('TRANSFORMERS_CACHE')}, HF_HOME={os.environ.get('HF_HOME')}")
            
            # Load model with simplified settings
            model = pipeline(
                task=task,
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,
                top_k=top_k,
                model_kwargs={
                    "cache_dir": str(CACHE_DIR),
                    "local_files_only": False
                }
            )
            
            # Debug: Check cache directory after loading
            logger.info(f"Cache directory contents after loading: {list(CACHE_DIR.glob('*'))}")
            
            # Cache the model
            model_cache[model_name] = model
            logger.info(f"Successfully loaded and cached model: {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise

def load_models_sequential():
    """Load models sequentially with better error handling"""
    try:
        logger.info("Starting model loading...")
        
        # Define models to load
        models_to_load = [
            ("j-hartmann/emotion-english-distilroberta-base", "emotion"),
            ("finiteautomata/bertweet-base-sentiment-analysis", "sentiment")
        ]
        
        results = {}
        for model_name, name in models_to_load:
            try:
                logger.info(f"Loading {name} model...")
                results[name] = load_model(model_name)
                logger.info(f"{name} model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load {name} model: {e}")
                raise
            
        logger.info("All models loaded successfully")
        return results["emotion"], results["sentiment"]
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise

# Load models before creating Flask app
logger.info("Initializing models...")
emotion_model, sentiment_model = load_models_sequential()
logger.info("Models initialized successfully")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

latest_results = {}

def translate_to_english(text):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text

@app.route('/receive', methods=['POST'])
def receive():
    global latest_results
    try:
        data = request.get_json()
        if not data:
            logger.warning("Received invalid JSON")
            return jsonify({"error": "Invalid JSON"}), 400

        user = data.get("user")
        message = data.get("message")
        logger.info(f"Received message from {user}: {message}")

        translated = translate_to_english(message)

        logger.info("=" * 40)
        logger.info(f"User       : {user}")
        logger.info(f"Message    : {message}")
        logger.info(f"Translated : {translated}")

        # Process models in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            emo_future = executor.submit(emotion_model, translated)
            sent_future = executor.submit(sentiment_model, translated)
            
            emo_result = emo_future.result()[0]
            sent_result = sent_future.result()[0]

        logger.info("\nEmotion results:")
        for e in emo_result:
            logger.info(f"  - {e['label']}: {e['score']:.2f}")
        logger.info("\nSentiment results:")
        for s in sent_result:
            logger.info(f"  - {s['label']}: {s['score']:.2f}")

        primary_emotion = emo_result[0]['label']
        primary_sentiment = sent_result[0]['label']
        
        logger.info(f"Selected emotion label: {primary_emotion}")
        logger.info(f"Selected sentiment label: {primary_sentiment}")
        logger.info("=" * 40)

        max_data = {
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
        socketio.emit('sentiment_event', max_data)

        return jsonify(max_data), 201
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting sentiment-api on port 6000...")
    try:
        # Test if we can bind to the port
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('0.0.0.0', 6000))
        test_socket.close()
        logger.info("Successfully bound to port 6000")
        
        # Start the server
        logger.info("Starting Flask-SocketIO server...")
        socketio.run(app, host='0.0.0.0', port=6000, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
