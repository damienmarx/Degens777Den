#!/bin/bash

# ==================== CLOUDFLARED TUNNEL SETUP ====================
# This script sets up a Cloudflare tunnel for hosting Degens777Den
# The tunnel allows secure access to your local/private backend via a public URL
# APK, Web App, and Discord webhooks will all work through this tunnel

set -e

echo "🌐 Degens777Den - Cloudflare Tunnel Setup"
echo "=========================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing cloudflared..."
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb
    echo "✅ cloudflared installed"
fi

echo ""
echo "🔐 Authenticating with Cloudflare..."
cloudflared tunnel login

echo ""
echo "🏗️  Creating tunnel 'kodakclout-prod'..."
cloudflared tunnel create kodakclout-prod || echo "Tunnel already exists"

echo ""
echo "📝 Creating tunnel configuration..."

# Create config directory if it doesn't exist
mkdir -p ~/.cloudflared

# Create tunnel config file
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: kodakclout-prod
credentials-file: /home/ubuntu/.cloudflared/kodakclout-prod.json

ingress:
  # Frontend (React App)
  - hostname: kodakclout-prod.workers.dev
    service: http://localhost:3000
    originRequest:
      httpHostHeader: localhost:3000
      noTLSVerify: false

  # Backend API
  - hostname: api.kodakclout-prod.workers.dev
    service: http://localhost:8001
    originRequest:
      httpHostHeader: localhost:8001
      noTLSVerify: false

  # WebSocket for live chat
  - hostname: ws.kodakclout-prod.workers.dev
    service: http://localhost:8001
    originRequest:
      httpHostHeader: localhost:8001
      noTLSVerify: false

  # Catch-all
  - service: http_status:404
EOF

echo "✅ Configuration created at ~/.cloudflared/config.yml"

echo ""
echo "🚀 Starting Cloudflare tunnel..."
echo ""
echo "Run this command to start the tunnel:"
echo ""
echo "  cloudflared tunnel run kodakclout-prod"
echo ""
echo "Or run it in the background:"
echo ""
echo "  nohup cloudflared tunnel run kodakclout-prod > /tmp/cloudflared.log 2>&1 &"
echo ""

echo "📱 Your APK will connect to:"
echo "  API: https://api.kodakclout-prod.workers.dev"
echo "  WebSocket: wss://ws.kodakclout-prod.workers.dev"
echo ""

echo "🌐 Your Web App will be available at:"
echo "  https://kodakclout-prod.workers.dev"
echo ""

echo "🤖 Discord webhooks will use:"
echo "  https://api.kodakclout-prod.workers.dev/api/..."
echo ""

echo "✨ Setup complete! Start the tunnel and your APK will work seamlessly."
