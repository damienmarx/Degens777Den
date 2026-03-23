#!/bin/bash
set -e

echo "=========================================="
echo "  DEGENS777DEN PRODUCTION SETUP"
echo "  Domain: cloutscape.org"
echo "  Tunnel: kodakclout-prod"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}[1/10] Updating system...${NC}"
apt-get update -qq
apt-get install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates lsb-release

echo -e "${GREEN}[2/10] Installing Node.js 20...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Install Yarn
if ! command -v yarn &> /dev/null; then
    npm install -g yarn
fi

echo -e "${GREEN}[3/10] Installing MongoDB...${NC}"
if ! command -v mongod &> /dev/null; then
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    apt-get update -qq
    apt-get install -y mongodb-org
fi

echo -e "${GREEN}[4/10] Configuring MongoDB with authentication...${NC}"
systemctl enable mongod
systemctl start mongod
sleep 3

# Create admin user
mongo << 'MONGOEOF' || true
use admin
db.createUser({
  user: "admin",
  pwd: "monalisa",
  roles: [ { role: "root", db: "admin" } ]
})
MONGOEOF

# Enable authentication
if ! grep -q "^security:" /etc/mongod.conf; then
    echo "security:" >> /etc/mongod.conf
    echo "  authorization: enabled" >> /etc/mongod.conf
fi

systemctl restart mongod
sleep 3

echo -e "${GREEN}[5/10] Installing Python 3.11 and dependencies...${NC}"
apt-get install -y python3.11 python3.11-venv python3-pip

echo -e "${GREEN}[6/10] Installing Cloudflared...${NC}"
if ! command -v cloudflared &> /dev/null; then
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
fi

echo -e "${GREEN}[7/10] Setting up application...${NC}"
APP_DIR="/opt/degensden"
mkdir -p $APP_DIR

# Copy application files
cp -r /app/backend $APP_DIR/
cp -r /app/frontend $APP_DIR/

# Setup Python virtual environment
cd $APP_DIR/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies and build
cd $APP_DIR/frontend
yarn install
yarn build

echo -e "${GREEN}[8/10] Configuring Supervisor...${NC}"
apt-get install -y supervisor

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
SUPEOF

supervisorctl reread
supervisorctl update
supervisorctl start all

echo -e "${GREEN}[9/10] Setting up Nginx...${NC}"
apt-get install -y nginx

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
nginx -t
systemctl restart nginx

echo -e "${GREEN}[10/10] Cloudflare Tunnel Setup...${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}MANUAL STEP REQUIRED:${NC}"
echo -e "1. Login to Cloudflare: ${GREEN}cloudflared tunnel login${NC}"
echo -e "2. Create tunnel: ${GREEN}cloudflared tunnel create kodakclout-prod${NC}"
echo -e "3. Route DNS: ${GREEN}cloudflared tunnel route dns kodakclout-prod cloutscape.org${NC}"
echo -e "4. Create config file at ${GREEN}~/.cloudflared/config.yml${NC}"
echo ""
echo -e "Example config.yml:"
echo -e "${YELLOW}---"
echo "tunnel: <YOUR-TUNNEL-ID>"
echo "credentials-file: /root/.cloudflared/<YOUR-TUNNEL-ID>.json"
echo ""
echo "ingress:"
echo "  - hostname: cloutscape.org"
echo "    service: http://localhost:80"
echo "  - service: http_status:404"
echo -e "---${NC}"
echo ""
echo -e "5. Start tunnel: ${GREEN}cloudflared tunnel run kodakclout-prod${NC}"
echo -e "6. Install as service: ${GREEN}cloudflared service install${NC}"
echo -e "${YELLOW}===========================================${NC}"

echo ""
echo -e "${GREEN}✅ DEGENS777DEN INSTALLATION COMPLETE!${NC}"
echo ""
echo "📊 Service Status:"
supervisorctl status

echo ""
echo "🔗 Access Points:"
echo "   Local: http://localhost"
echo "   Production: https://cloutscape.org (after Cloudflare setup)"
echo ""
echo "🗄️  MongoDB:"
echo "   URL: mongodb://admin:monalisa@localhost:27017/?authSource=admin"
echo "   Database: degensden_casino"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f /var/log/supervisor/degensden-backend.*.log"
echo "   Frontend: tail -f /var/log/supervisor/degensden-frontend.*.log"
echo ""
echo "🎮 Seed admin user:"
echo "   curl -X POST http://localhost:8001/api/seed"
echo ""
echo -e "${YELLOW}⚠️  Don't forget to complete Cloudflare tunnel setup!${NC}"
echo ""
