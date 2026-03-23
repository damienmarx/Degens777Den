#!/bin/bash

# ==================== DEGENS777DEN PRODUCTION DEPLOYMENT ====================
# Complete deployment script for APK + Web + Backend + Cloudflare Tunnel
# Usage: bash deploy-production.sh

set -e

echo "🚀 Degens777Den - Production Deployment"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/ubuntu/Degens777Den"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
TUNNEL_NAME="kodakclout-prod"

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# ==================== STEP 1: VERIFY PREREQUISITES ====================
echo ""
echo "📋 Step 1: Verifying Prerequisites"
echo "-----------------------------------"

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ] && [ "$EUID" != 0 ]; then
    print_error "This script should be run as 'ubuntu' user or with sudo"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js not found. Please install Node.js 20+"
    exit 1
fi
print_status "Node.js $(node -v) found"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm not found"
    exit 1
fi
print_status "npm $(npm -v) found"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    exit 1
fi
print_status "Python $(python3 --version) found"

# Check MongoDB
if ! command -v mongod &> /dev/null; then
    print_error "MongoDB not found. Please install MongoDB"
    exit 1
fi
print_status "MongoDB found"

# Check git
if ! command -v git &> /dev/null; then
    print_error "Git not found"
    exit 1
fi
print_status "Git found"

# ==================== STEP 2: SETUP BACKEND ====================
echo ""
echo "🔧 Step 2: Setting Up Backend"
echo "-----------------------------"

cd "$BACKEND_DIR"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt -q

print_status "Backend dependencies installed"

# ==================== STEP 3: SETUP FRONTEND ====================
echo ""
echo "🎨 Step 3: Setting Up Frontend"
echo "------------------------------"

cd "$FRONTEND_DIR"

# Install dependencies
print_info "Installing Node.js dependencies..."
npm install --legacy-peer-deps -q

# Build for production
print_info "Building frontend for production..."
npm run build -q

print_status "Frontend built successfully"

# ==================== STEP 4: SETUP CLOUDFLARE TUNNEL ====================
echo ""
echo "🌐 Step 4: Setting Up Cloudflare Tunnel"
echo "--------------------------------------"

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    print_info "Installing cloudflared..."
    curl -L --output /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb 2>/dev/null
    sudo dpkg -i /tmp/cloudflared.deb -q
    rm /tmp/cloudflared.deb
    print_status "cloudflared installed"
else
    print_status "cloudflared already installed"
fi

# Check if tunnel exists
if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    print_status "Tunnel '$TUNNEL_NAME' already exists"
else
    print_info "Creating tunnel '$TUNNEL_NAME'..."
    cloudflared tunnel create "$TUNNEL_NAME" -q
    print_status "Tunnel created"
fi

# ==================== STEP 5: SETUP SYSTEMD SERVICES ====================
echo ""
echo "⚙️  Step 5: Setting Up Systemd Services"
echo "-------------------------------------"

# Install backend service
print_info "Installing backend service..."
sudo cp "$PROJECT_DIR/degens-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable degens-backend.service
print_status "Backend service installed"

# ==================== STEP 6: ENVIRONMENT CONFIGURATION ====================
echo ""
echo "🔐 Step 6: Verifying Environment Configuration"
echo "---------------------------------------------"

# Check if .env exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    print_error ".env file not found in backend directory"
    print_info "Please create $BACKEND_DIR/.env with required configuration"
    exit 1
fi

# Verify critical env variables
REQUIRED_VARS=("MONGO_URL" "JWT_SECRET" "DISCORD_WEBHOOK_URL")
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "$var" "$BACKEND_DIR/.env"; then
        print_error "Missing $var in .env file"
    else
        print_status "$var configured"
    fi
done

# ==================== STEP 7: START SERVICES ====================
echo ""
echo "🚀 Step 7: Starting Services"
echo "----------------------------"

# Start MongoDB
print_info "Starting MongoDB..."
sudo systemctl start mongod
sudo systemctl enable mongod
print_status "MongoDB started"

# Start backend
print_info "Starting backend API..."
sudo systemctl start degens-backend.service
sleep 2
if sudo systemctl is-active --quiet degens-backend.service; then
    print_status "Backend API started"
else
    print_error "Failed to start backend API"
    sudo systemctl status degens-backend.service
    exit 1
fi

# Start tunnel (in background)
print_info "Starting Cloudflare tunnel..."
nohup cloudflared tunnel run "$TUNNEL_NAME" > /tmp/cloudflared.log 2>&1 &
sleep 2
print_status "Cloudflare tunnel started"

# ==================== STEP 8: VERIFICATION ====================
echo ""
echo "✅ Step 8: Verifying Deployment"
echo "-------------------------------"

# Check backend
print_info "Checking backend..."
if curl -s http://localhost:8001/api/health &> /dev/null || curl -s http://localhost:8001 &> /dev/null; then
    print_status "Backend API is responding"
else
    print_error "Backend API is not responding"
fi

# Check MongoDB
print_info "Checking MongoDB..."
if mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
    print_status "MongoDB is running"
else
    print_error "MongoDB is not responding"
fi

# Check tunnel
print_info "Checking Cloudflare tunnel..."
if cloudflared tunnel info "$TUNNEL_NAME" &> /dev/null; then
    print_status "Cloudflare tunnel is active"
else
    print_error "Cloudflare tunnel status unknown"
fi

# ==================== STEP 9: SUMMARY ====================
echo ""
echo "📊 Deployment Summary"
echo "====================
"

echo "Backend:"
echo "  URL: http://localhost:8001"
echo "  Status: $(sudo systemctl is-active degens-backend.service)"
echo "  Logs: sudo journalctl -u degens-backend.service -f"
echo ""

echo "Frontend:"
echo "  Build: $FRONTEND_DIR/build"
echo "  Status: Ready for deployment"
echo ""

echo "Cloudflare Tunnel:"
echo "  Name: $TUNNEL_NAME"
echo "  Public URL: https://$TUNNEL_NAME.workers.dev"
echo "  Logs: tail -f /tmp/cloudflared.log"
echo ""

echo "MongoDB:"
echo "  Status: $(sudo systemctl is-active mongod)"
echo "  Logs: sudo journalctl -u mongod -f"
echo ""

# ==================== STEP 10: NEXT STEPS ====================
echo ""
echo "🎯 Next Steps"
echo "============="
echo ""
echo "1. Build APK:"
echo "   cd $FRONTEND_DIR"
echo "   npm install -g @capacitor/cli"
echo "   npx cap add android"
echo "   npx cap copy"
echo "   cd android && ./gradlew assembleRelease"
echo ""
echo "2. Test Web App:"
echo "   Open https://$TUNNEL_NAME.workers.dev in your browser"
echo ""
echo "3. Install APK on Android:"
echo "   adb install -r app-release.apk"
echo ""
echo "4. Monitor Services:"
echo "   sudo systemctl status degens-backend.service"
echo "   sudo systemctl status mongod"
echo "   cloudflared tunnel logs $TUNNEL_NAME"
echo ""
echo "5. View Logs:"
echo "   Backend: sudo journalctl -u degens-backend.service -f"
echo "   MongoDB: sudo journalctl -u mongod -f"
echo "   Tunnel: tail -f /tmp/cloudflared.log"
echo ""

print_status "Deployment complete!"
echo ""
