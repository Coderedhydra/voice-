#!/bin/bash
# Production deployment script for Ubuntu

set -e  # Exit on any error

echo "🚀 Deploying Live Interview Assistant Backend on Ubuntu"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# 1. Install system dependencies
echo -e "\n${GREEN}[1/8]${NC} Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx curl

# 2. Install Ollama
echo -e "\n${GREEN}[2/8]${NC} Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "Ollama already installed"
fi

# 3. Start Ollama service
echo -e "\n${GREEN}[3/8]${NC} Starting Ollama service..."
systemctl enable ollama
systemctl start ollama
sleep 3

# 4. Pull the model
echo -e "\n${GREEN}[4/8]${NC} Pulling SmolLM2 1.7B model..."
ollama pull smollm2:1.7b

# 5. Create deployment directory
echo -e "\n${GREEN}[5/8]${NC} Setting up application directory..."
DEPLOY_DIR="/opt/voice-assistant"
mkdir -p $DEPLOY_DIR
cp -r . $DEPLOY_DIR/backend/
cd $DEPLOY_DIR/backend

# 6. Setup Python environment
echo -e "\n${GREEN}[6/8]${NC} Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Setup environment file
echo -e "\n${GREEN}[7/8]${NC} Configuring environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit /opt/voice-assistant/backend/.env with your configuration${NC}"
fi

# 8. Setup systemd service
echo -e "\n${GREEN}[8/8]${NC} Setting up systemd service..."
cp voice-assistant.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable voice-assistant.service
systemctl start voice-assistant.service

# Optional: Setup Nginx
read -p "Do you want to setup Nginx reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp nginx.conf /etc/nginx/sites-available/voice-assistant
    ln -sf /etc/nginx/sites-available/voice-assistant /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    echo -e "${GREEN}✓ Nginx configured${NC}"
fi

# Check status
echo -e "\n${GREEN}✓ Deployment complete!${NC}"
echo -e "\nService status:"
systemctl status voice-assistant.service --no-pager

echo -e "\n${GREEN}Access the API at:${NC}"
echo "  - Health check: http://localhost:5000/health"
echo "  - API endpoint: http://localhost:5000/ask"

echo -e "\n${YELLOW}Useful commands:${NC}"
echo "  - View logs: sudo journalctl -u voice-assistant.service -f"
echo "  - Restart service: sudo systemctl restart voice-assistant.service"
echo "  - Stop service: sudo systemctl stop voice-assistant.service"
