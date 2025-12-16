# Backend Setup (Ubuntu + Ollama)

Production-ready backend for Live Interview Assistant using Flask and Ollama AI.

---

## Quick Start (Development)

```bash
cd backend
chmod +x setup_ollama.sh
./setup_ollama.sh
source venv/bin/activate
python app.py
```

Visit: http://localhost:5000/health

---

## Prerequisites

### 1. Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Start Ollama Service
```bash
# Option A: Run as service (recommended)
sudo systemctl enable ollama
sudo systemctl start ollama

# Option B: Run manually
ollama serve
```

### 3. Pull the AI Model
```bash
ollama pull smollm2:1.7b
```

---

## Development Setup

### Manual Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run development server**
   ```bash
   # Using Flask dev server
   python app.py
   
   # Using Gunicorn with auto-reload
   gunicorn --bind 0.0.0.0:5000 --reload app:app
   ```

---

## Production Deployment

### Automated Deployment
```bash
sudo chmod +x deploy_ubuntu.sh
sudo ./deploy_ubuntu.sh
```

This will:
- ✅ Install system dependencies
- ✅ Setup Ollama and download models
- ✅ Create systemd service
- ✅ Configure Nginx (optional)
- ✅ Setup auto-restart on failure

### Manual Production Setup

1. **Install as systemd service**
   ```bash
   sudo cp voice-assistant.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable voice-assistant.service
   sudo systemctl start voice-assistant.service
   ```

2. **Setup Nginx reverse proxy** (optional)
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/voice-assistant
   sudo ln -s /etc/nginx/sites-available/voice-assistant /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **View logs**
   ```bash
   # Service logs
   sudo journalctl -u voice-assistant.service -f
   
   # Application logs (if using gunicorn config)
   tail -f /var/log/voice-assistant/error.log
   ```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=smollm2:1.7b

# Flask Configuration
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Model Parameters
MAX_TOKENS=200
TEMPERATURE=0.7

# CORS (comma-separated origins, or * for all)
ALLOWED_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

### Using Different Models

To use a different Ollama model:
```bash
# Pull a different model
ollama pull llama2:7b

# Update .env
OLLAMA_MODEL=llama2:7b
```

Available small models:
- `smollm2:1.7b` (recommended, fastest)
- `tinyllama:1.1b` (smallest)
- `phi:2.7b` (more capable)

---

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "model": "smollm2:1.7b",
  "ollama_host": "http://localhost:11434",
  "available_models": 3
}
```

### Ask Question
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"text": "What is Python?"}'
```

Response:
```json
{
  "answer": "Python is a high-level programming language..."
}
```

---

## Ubuntu-Specific Optimizations

### 1. **Systemd Service**
Auto-restart on failure, proper user isolation, dependency management

### 2. **Gunicorn WSGI Server**
Production-grade server with:
- Multi-worker support
- Graceful reloads
- Request timeouts optimized for AI

### 3. **Nginx Reverse Proxy**
- Rate limiting (10 req/s)
- Proper timeout handling (120s for AI)
- CORS headers
- Request logging

### 4. **Resource Management**
```bash
# Check Ollama GPU usage
ollama ps

# Monitor system resources
htop

# Check service status
systemctl status voice-assistant.service ollama.service
```

---

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
systemctl status ollama

# Test Ollama directly
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama
```

### Port Already in Use
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process or change FLASK_PORT in .env
```

### Model Not Found
```bash
# List available models
ollama list

# Pull the model
ollama pull smollm2:1.7b
```

### Permission Issues
```bash
# Create log directory
sudo mkdir -p /var/log/voice-assistant
sudo chown www-data:www-data /var/log/voice-assistant

# Fix deployment directory permissions
sudo chown -R www-data:www-data /opt/voice-assistant
```

---

## Performance Tips

1. **Use GPU acceleration** (if available)
   ```bash
   # Ollama automatically uses GPU if available
   # Check with: nvidia-smi
   ```

2. **Optimize worker count**
   ```python
   # In gunicorn_config.py
   workers = (2 * cpu_count) + 1
   ```

3. **Enable model caching**
   - Ollama keeps models in memory after first use
   - Restart only when necessary

4. **Monitor memory usage**
   ```bash
   # 1.7B model uses ~2-3GB RAM
   free -h
   ```

---

## Useful Commands

```bash
# Service management
sudo systemctl start voice-assistant.service
sudo systemctl stop voice-assistant.service
sudo systemctl restart voice-assistant.service
sudo systemctl status voice-assistant.service

# View logs
sudo journalctl -u voice-assistant.service -f
sudo journalctl -u ollama.service -f

# Test API
curl http://localhost:5000/health
curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d '{"text":"test"}'

# Ollama management
ollama list                    # List models
ollama pull smollm2:1.7b      # Download model
ollama rm smollm2:1.7b        # Remove model
ollama ps                      # Show running models
```

---

## Frontend Integration

Update your frontend's `BACKEND_URL`:

**Development:**
```javascript
const BACKEND_URL = 'http://localhost:5000';
```

**Production (with Nginx):**
```javascript
const BACKEND_URL = 'https://your-domain.com/api';
```

---

## Security Recommendations

1. **Firewall setup**
   ```bash
   sudo ufw allow 5000/tcp  # Only if not using Nginx
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

2. **HTTPS with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

3. **Rate limiting** - Already configured in `nginx.conf`

4. **Environment variables** - Never commit `.env` to git

---

## Support

For issues:
1. Check logs: `sudo journalctl -u voice-assistant.service -f`
2. Verify Ollama: `curl http://localhost:11434/api/tags`
3. Test health: `curl http://localhost:5000/health`
