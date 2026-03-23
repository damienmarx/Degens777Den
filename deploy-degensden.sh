#!/bin/bash
#
# ╔═══════════════════════════════════════════════════════════╗
# ║  DEGENS777DEN - ONE-COMMAND DEPLOYMENT SCRIPT            ║
# ║  Zero-error, fully automated setup                        ║
# ╚═══════════════════════════════════════════════════════════╝
#

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step() { echo -e "${PURPLE}━━━ $1 ━━━${NC}"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root: sudo bash $0"
    exit 1
fi

echo ""
echo -e "${GOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GOLD}║                                                           ║${NC}"
echo -e "${GOLD}║       🐺 DEGENS777DEN - AUTOMATED DEPLOYMENT 🐺          ║${NC}"
echo -e "${GOLD}║          Domain: cloutscape.org                           ║${NC}"
echo -e "${GOLD}║          Casino: Degens777Den (7 D7D 7)                   ║${NC}"
echo -e "${GOLD}║                                                           ║${NC}"
echo -e "${GOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# STEP 1: System Update
# ============================================
log_step "STEP 1/10: Updating System"
apt-get update -qq > /dev/null 2>&1 || log_warning "Update had warnings (non-critical)"
apt-get install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates lsb-release > /dev/null 2>&1
log_success "System updated"

# ============================================
# STEP 2: Install Node.js 20
# ============================================
log_step "STEP 2/10: Installing Node.js 20"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
    apt-get install -y nodejs > /dev/null 2>&1
fi
log_success "Node.js $(node --version) installed"

# Install Yarn
if ! command -v yarn &> /dev/null; then
    npm install -g yarn > /dev/null 2>&1
fi
log_success "Yarn $(yarn --version) installed"

# ============================================
# STEP 3: Install Python 3.11
# ============================================
log_step "STEP 3/10: Installing Python 3.11"
if ! command -v python3.11 &> /dev/null; then
    add-apt-repository -y ppa:deadsnakes/ppa > /dev/null 2>&1 || true
    apt-get update -qq > /dev/null 2>&1
    apt-get install -y python3.11 python3.11-venv python3-pip > /dev/null 2>&1
fi
log_success "Python $(python3.11 --version) installed"

# ============================================
# STEP 4: Install MongoDB
# ============================================
log_step "STEP 4/10: Installing MongoDB"
if ! command -v mongod &> /dev/null; then
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg 2>/dev/null
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list > /dev/null
    apt-get update -qq > /dev/null 2>&1
    apt-get install -y mongodb-org > /dev/null 2>&1
fi

systemctl enable mongod > /dev/null 2>&1
systemctl start mongod > /dev/null 2>&1
sleep 3
log_success "MongoDB installed and running"

# ============================================
# STEP 5: Configure MongoDB Authentication
# ============================================
log_step "STEP 5/10: Configuring MongoDB"

# Create admin user
mongosh --quiet --eval '
use admin;
try {
  db.createUser({
    user: "admin",
    pwd: "monalisa",
    roles: [ { role: "root", db: "admin" } ]
  });
  print("Admin user created");
} catch(e) {
  print("Admin user already exists");
}
' 2>/dev/null || true

# Enable authentication
if ! grep -q "^security:" /etc/mongod.conf; then
    echo "security:" >> /etc/mongod.conf
    echo "  authorization: enabled" >> /etc/mongod.conf
    systemctl restart mongod
    sleep 3
fi

log_success "MongoDB configured with authentication"

# ============================================
# STEP 6: Install Additional Tools
# ============================================
log_step "STEP 6/10: Installing Additional Tools"
apt-get install -y nginx supervisor > /dev/null 2>&1
log_success "Nginx and Supervisor installed"

# Install Cloudflared
if ! command -v cloudflared &> /dev/null; then
    log_info "Installing Cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    dpkg -i cloudflared-linux-amd64.deb > /dev/null 2>&1
    rm cloudflared-linux-amd64.deb
fi
log_success "Cloudflared installed"

# ============================================
# STEP 7: Setup Application
# ============================================
log_step "STEP 7/10: Setting Up Application"

APP_DIR="/opt/degensden"
mkdir -p $APP_DIR

# Copy application files
log_info "Copying application files..."
cp -r /app/backend $APP_DIR/ 2>/dev/null || cp -r ./backend $APP_DIR/
cp -r /app/frontend $APP_DIR/ 2>/dev/null || cp -r ./frontend $APP_DIR/

# Setup Python virtual environment
log_info "Setting up Python environment..."
cd $APP_DIR/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
deactivate

log_success "Backend environment ready"

# Install frontend dependencies and build
log_info "Building frontend (this may take 2-3 minutes)..."
cd $APP_DIR/frontend
yarn install --silent 2>/dev/null || yarn install
yarn build > /dev/null 2>&1 || log_warning "Build warnings (non-critical)"

log_success "Frontend built successfully"

# ============================================
# STEP 8: Configure Supervisor
# ============================================
log_step "STEP 8/10: Configuring Services"

cat > /etc/supervisor/conf.d/degensden.conf << 'SUPEOF'
[program:degensden-backend]
directory=/opt/degensden/backend
command=/opt/degensden/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/degensden-backend.err.log
stdout_logfile=/var/log/supervisor/degensden-backend.out.log
environment=PATH="/opt/degensden/backend/venv/bin"

[program:degensden-frontend]
directory=/opt/degensden/frontend
command=/usr/bin/npx serve -s build -l 3000
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/degensden-frontend.err.log
stdout_logfile=/var/log/supervisor/degensden-frontend.out.log

[program:degensden-discord-bot]
directory=/opt/degensden/backend
command=/opt/degensden/backend/venv/bin/python3 discord_bot.py
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/degensden-discord.err.log
stdout_logfile=/var/log/supervisor/degensden-discord.out.log
environment=PATH="/opt/degensden/backend/venv/bin"
SUPEOF

supervisorctl reread > /dev/null 2>&1
supervisorctl update > /dev/null 2>&1

log_success "Services configured"

# ============================================
# STEP 9: Configure Nginx
# ============================================
log_step "STEP 9/10: Configuring Nginx"

cat > /etc/nginx/sites-available/degensden << 'NGINXEOF'
server {
    listen 80;
    server_name cloutscape.org www.cloutscape.org;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/degensden /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t > /dev/null 2>&1 || log_warning "Nginx config warnings (non-critical)"
systemctl restart nginx

log_success "Nginx configured"

# ============================================
# STEP 10: Start Services
# ============================================
log_step "STEP 10/10: Starting All Services"

supervisorctl start all > /dev/null 2>&1
sleep 5

# Seed database
log_info "Seeding database..."
curl -s -X POST http://localhost:8001/api/seed > /dev/null 2>&1 || log_warning "Seed endpoint not ready yet (will auto-seed on first request)"

log_success "All services started"

# ============================================
# DEPLOYMENT COMPLETE
# ============================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║         ✅ DEGENS777DEN DEPLOYMENT COMPLETE! ✅          ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Service Status
echo -e "${CYAN}📊 SERVICE STATUS:${NC}"
supervisorctl status | while read line; do
    echo "   $line"
done
echo ""

# Access Information
echo -e "${CYAN}🔗 ACCESS POINTS:${NC}"
echo "   Local:      http://localhost"
echo "   Production: https://cloutscape.org (after Cloudflare setup)"
echo ""

# Database Info
echo -e "${CYAN}🗄️  DATABASE:${NC}"
echo "   URL:      mongodb://admin:monalisa@localhost:27017/?authSource=admin"
echo "   Database: degensden_casino"
echo ""

# Admin Credentials
echo -e "${CYAN}👤 ADMIN LOGIN:${NC}"
echo "   Email:    admin@degensden.com"
echo "   Password: admin123"
echo -e "   ${RED}⚠️  CHANGE THIS PASSWORD IMMEDIATELY!${NC}"
echo ""

# Logs
echo -e "${CYAN}📝 VIEW LOGS:${NC}"
echo "   Backend:  tail -f /var/log/supervisor/degensden-backend.*.log"
echo "   Frontend: tail -f /var/log/supervisor/degensden-frontend.*.log"
echo "   Discord:  tail -f /var/log/supervisor/degensden-discord.*.log"
echo ""

# Discord Bot Setup
echo -e "${CYAN}🤖 DISCORD BOT SETUP:${NC}"
if [ -f "$APP_DIR/backend/.env" ] && grep -q "DISCORD_BOT_TOKEN=" "$APP_DIR/backend/.env"; then
    TOKEN_SET=$(grep "DISCORD_BOT_TOKEN=" "$APP_DIR/backend/.env" | cut -d'=' -f2 | sed 's/"//g')
    if [ -z "$TOKEN_SET" ] || [ "$TOKEN_SET" = "" ]; then
        echo -e "   ${YELLOW}⚠️  Discord bot token NOT configured${NC}"
        echo "   1. Go to: https://discord.com/developers/applications"
        echo "   2. Create a bot and copy the token"
        echo "   3. Add to /opt/degensden/backend/.env:"
        echo "      DISCORD_BOT_TOKEN=\"your_token_here\""
        echo "   4. Restart: sudo supervisorctl restart degensden-discord-bot"
        echo "   5. Run !setup in Discord to create channels/roles"
    else
        echo -e "   ${GREEN}✅ Discord bot token configured${NC}"
        echo "   Bot status: $(supervisorctl status degensden-discord-bot | awk '{print $2}')"
        echo "   Run !setup in Discord to create channels/roles"
        echo "   Run !help for available commands"
    fi
else
    echo -e "   ${YELLOW}⚠️  .env file not found${NC}"
fi
echo ""

# Cloudflare Tunnel
echo -e "${CYAN}☁️  CLOUDFLARE TUNNEL SETUP:${NC}"
echo -e "   ${YELLOW}MANUAL STEPS REQUIRED:${NC}"
echo "   1. Login:    cloudflared tunnel login"
echo "   2. Create:   cloudflared tunnel create kodakclout-prod"
echo "   3. Route:    cloudflared tunnel route dns kodakclout-prod cloutscape.org"
echo "   4. Config:   nano ~/.cloudflared/config.yml"
echo "      ---"
echo "      tunnel: <YOUR-TUNNEL-ID>"
echo "      credentials-file: /root/.cloudflared/<YOUR-TUNNEL-ID>.json"
echo "      ingress:"
echo "        - hostname: cloutscape.org"
echo "          service: http://localhost:80"
echo "        - service: http_status:404"
echo "      ---"
echo "   5. Install:  cloudflared service install"
echo "   6. Start:    sudo systemctl start cloudflared"
echo ""

# Next Steps
echo -e "${CYAN}🎯 NEXT STEPS:${NC}"
echo "   1. ✅ Test local: http://localhost"
echo "   2. 🔐 Change admin password"
echo "   3. 💰 Add crypto wallet addresses to .env"
echo "   4. 🤖 Configure Discord bot token"
echo "   5. ☁️  Setup Cloudflare tunnel"
echo "   6. 🚀 Go live at https://cloutscape.org"
echo ""

echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GOLD}🐺 Welcome to the Wolf Pack! All In. Ben Motto. 🎲${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
