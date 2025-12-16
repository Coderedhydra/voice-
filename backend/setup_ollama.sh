#!/bin/bash
# Quick setup script for Ubuntu development environment

set -e

echo "🔧 Setting up development environment on Ubuntu"
echo "==============================================="

# 1. Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✓ Ollama already installed"
fi

# 2. Start Ollama
echo "Starting Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
    sleep 3
    echo "✓ Ollama server started"
else
    echo "✓ Ollama already running"
fi

# 3. Pull the model
echo "Pulling SmolLM2 1.7B model (this may take a few minutes)..."
ollama pull smollm2:1.7b

# 4. Create virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python app.py"
echo ""
echo "Or use Gunicorn for production-like testing:"
echo "  gunicorn --bind 0.0.0.0:5000 --reload app:app"
