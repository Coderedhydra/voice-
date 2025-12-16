from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# CORS Configuration
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins == '*':
    CORS(app)
else:
    origins_list = [origin.strip() for origin in allowed_origins.split(',')]
    CORS(app, origins=origins_list)

# Configuration from environment variables
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
MODEL_NAME = os.getenv('OLLAMA_MODEL', 'smollm2:1.7b')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '200'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))

# Configure Ollama client
client = ollama.Client(host=OLLAMA_HOST)

# Test Ollama connection on startup
try:
    logger.info(f"Testing connection to Ollama at {OLLAMA_HOST}")
    logger.info(f"Using model: {MODEL_NAME}")
    models = client.list()
    logger.info(f"✓ Ollama connection successful! Available models: {len(models.get('models', []))}")
    
    # Check if the specific model is available
    model_names = [m['name'] for m in models.get('models', [])]
    if MODEL_NAME not in model_names and f"{MODEL_NAME}:latest" not in model_names:
        logger.warning(f"⚠️  Model '{MODEL_NAME}' not found. Run: ollama pull {MODEL_NAME}")
    else:
        logger.info(f"✓ Model '{MODEL_NAME}' is ready!")
except Exception as e:
    logger.error(f"✗ Failed to connect to Ollama: {e}")
    logger.error("Please ensure Ollama is running: 'sudo systemctl start ollama' or 'ollama serve'")

@app.route("/", methods=["GET"])
def index():
    """API information endpoint"""
    return jsonify({
        "service": "Live Interview Assistant API",
        "version": "1.0.0",
        "status": "running",
        "model": MODEL_NAME,
        "endpoints": {
            "GET /": "API information (this page)",
            "GET /health": "Health check endpoint",
            "POST /ask": "Ask a question (requires JSON body with 'text' field)"
        },
        "example_usage": {
            "health_check": "curl http://localhost:5000/health",
            "ask_question": "curl -X POST http://localhost:5000/ask -H 'Content-Type: application/json' -d '{\"text\":\"What is Python?\"}'"
        }
    }), 200

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        models = client.list()
        return jsonify({
            "status": "healthy",
            "model": MODEL_NAME,
            "ollama_host": OLLAMA_HOST,
            "available_models": len(models.get('models', []))
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "ollama_host": OLLAMA_HOST
        }), 503

@app.route("/ask", methods=["POST"])
def ask():
    """Generate answer for interview question"""
    data = request.get_json()
    question = data.get("text", "").strip()
    
    if not question:
        return jsonify({"answer": "No question provided."}), 400

    try:
        logger.info(f"Processing question: {question[:50]}...")
        
        # Create a prompt for interview context
        prompt = f"You are an interview assistant. Answer this question concisely and professionally:\n\nQuestion: {question}\n\nAnswer:"
        
        # Generate response using Ollama
        response = client.generate(
            model=MODEL_NAME,
            prompt=prompt,
            options={
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS,
            }
        )
        
        answer = response['response'].strip()
        logger.info(f"Generated answer: {answer[:50]}...")
        
        return jsonify({"answer": answer}), 200
        
    except ollama.ResponseError as e:
        logger.error(f"Ollama response error: {e}")
        return jsonify({"answer": f"Model error: {e.error}"}), 500
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return jsonify({"answer": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Live Interview Assistant Backend")
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"Ollama Host: {OLLAMA_HOST}")
    logger.info(f"Max Tokens: {MAX_TOKENS} | Temperature: {TEMPERATURE}")
    logger.info("=" * 60)
    
    # Get host and port from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_ENV', 'production') != 'production'
    
    app.run(host=host, port=port, debug=debug)
