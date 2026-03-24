#!/bin/bash

# --- Configuration Variables ---
APP_DIR="/opt/degensden"
LOG_DIR="/var/log/degensden"
NGINX_CONF_PATH="/etc/nginx/sites-available/degensden"

# --- Colors for better output ---
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
CYAN=\033[0;36m
NC=\033[0m # No Color

# --- Logging Functions ---
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
log_step() { echo -e "\n${PURPLE}--- $1 ---${NC}"; }

# --- Pre-requisite Checks and Installations ---
check_and_install_docker() {
    log_step "Checking and Installing Docker & Docker Compose"
    if ! command -v docker &> /dev/null; then
        log_info "Docker not found. Installing Docker..."
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl gnupg
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        echo \
          "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          \$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
          sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        sudo usermod -aG docker $USER
        log_success "Docker installed. Please log out and log back in for Docker group changes to take effect, then re-run this script."
        exit 0
    else
        log_success "Docker already installed."
    fi

    if ! command -v docker compose &> /dev/null; then
        log_info "Docker Compose (plugin) not found. It should be installed with Docker Engine."
        log_warning "If you encounter issues, please install it manually: https://docs.docker.com/compose/install/"
    else
        log_success "Docker Compose already installed."
    fi
}

check_and_install_cloudflared() {
    log_step "Checking and Installing Cloudflared"
    if ! command -v cloudflared &> /dev/null; then
        log_info "Cloudflared not found. Installing Cloudflared..."
        curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
        sudo dpkg -i cloudflared.deb
        rm cloudflared.deb
        log_success "Cloudflared installed."
    else
        log_success "Cloudflared already installed."
    fi
}

# --- Main Deployment Logic ---
deploy_application() {
    log_step "Starting Degens777Den Deployment"

    # Create application directory
    sudo mkdir -p $APP_DIR
    sudo chown -R $USER:$USER $APP_DIR
    cp -r . $APP_DIR/
    cd $APP_DIR

    # Create log directory
    sudo mkdir -p $LOG_DIR
    sudo chown -R $USER:$USER $LOG_DIR

    # --- Environment Variables ---
    log_step "Setting up Environment Variables"
    if [ ! -f "$APP_DIR/backend/.env" ]; then
        log_info "No .env file found for backend. Creating one from .env.production template."
        cp "$APP_DIR/backend/.env.production" "$APP_DIR/backend/.env"
        log_warning "Please edit $APP_DIR/backend/.env with your actual production secrets (e.g., MONGO_URL, JWT_SECRET, DISCORD_BOT_TOKEN, COINBASE_API_KEY, etc.)."
        log_warning "Default admin credentials are admin@degensden.com / admin123. CHANGE THEM IMMEDIATELY!"
    else
        log_success "Backend .env file already exists."
    fi

    # --- Docker Compose Build and Run ---
    log_step "Building and Running Docker Containers"
    docker compose build
    docker compose up -d

    log_info "Waiting for services to become healthy..."
    # Wait for backend service to be healthy
    docker compose ps | grep degensden-backend | grep -q "healthy"
    while [ $? -ne 0 ]; do
        echo -n "."
        sleep 5
        docker compose ps | grep degensden-backend | grep -q "healthy"
    done
    log_success "Backend service is healthy."

    # Wait for frontend service to be healthy
    docker compose ps | grep degensden-frontend | grep -q "healthy"
    while [ $? -ne 0 ]; do
        echo -n "."
        sleep 5
        docker compose ps | grep degensden-frontend | grep -q "healthy"
    done
    log_success "Frontend service is healthy."

    log_success "All core services are up and healthy."

    # --- Nginx Configuration (if not using Cloudflare Tunnel for direct exposure) ---
    log_step "Configuring Nginx (for local access or if Cloudflare Tunnel is not used)"
    sudo cp "$APP_DIR/nginx.conf" "/etc/nginx/nginx.conf"
    sudo nginx -t > /dev/null 2>&1 || log_warning "Nginx config warnings (non-critical)"
    sudo systemctl restart nginx
    log_success "Nginx configured and restarted."

    # --- Cloudflare Tunnel Setup ---
    log_step "Setting up Cloudflare Tunnel (Optional for Public Access)"
    read -p "Do you want to set up Cloudflare Tunnel for public access (y/N)? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cloudflare Tunnel setup initiated."
        log_warning "You will need to have a Cloudflare account and a domain added to it."
        log_warning "Please follow the interactive prompts from cloudflared."

        # Authenticate cloudflared with Cloudflare account
        cloudflared tunnel login

        # Prompt for tunnel name and domain
        read -p "Enter your desired Cloudflare Tunnel name (e.g., degensden-prod): " TUNNEL_NAME
        read -p "Enter your domain (e.g., cloutscape.org): " APP_DOMAIN

        # Create a tunnel
        cloudflared tunnel create $TUNNEL_NAME

        # Get tunnel ID (this requires parsing cloudflared output, which can be brittle)
        # For simplicity, we'll ask the user to manually get the ID or rely on the config file.
        log_warning "Please copy your Tunnel ID from the cloudflared output above or from ~/.cloudflared/<TUNNEL_NAME>.json."
        read -p "Enter your Cloudflare Tunnel ID: " TUNNEL_ID

        # Route DNS
        cloudflared tunnel route dns $TUNNEL_NAME $APP_DOMAIN

        # Create config.yml for the tunnel
        mkdir -p ~/.cloudflared
        cat <<EOF > ~/.cloudflared/config.yml
tunnel: $TUNNEL_ID
credentials-file: /root/.cloudflared/$TUNNEL_ID.json
ingress:
  - hostname: $APP_DOMAIN
    service: http://localhost:80
  - service: http_status:404
EOF
        log_success "Cloudflare Tunnel config.yml created at ~/.cloudflared/config.yml."

        # Install and run the tunnel as a service
        sudo cloudflared service install
        sudo systemctl start cloudflared
        sudo systemctl enable cloudflared
        log_success "Cloudflare Tunnel service installed and started."
        log_success "Your application should now be publicly accessible at https://$APP_DOMAIN."
    else
        log_info "Cloudflare Tunnel setup skipped. Application accessible locally via Docker ports."
    fi

    log_success "Degens777Den Deployment Complete!"
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║         ✅ DEGENS777DEN DEPLOYMENT COMPLETE! ✅          ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📊 SERVICE STATUS:${NC}"
    docker compose ps
    echo ""
    echo -e "${CYAN}🔗 ACCESS POINTS:${NC}"
    echo "   Local Frontend: http://localhost:3000"
    echo "   Local Backend API: http://localhost:8000/api"
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Public (via Cloudflare Tunnel): https://$APP_DOMAIN"
    fi
    echo ""
    echo -e "${CYAN}👤 ADMIN LOGIN (CHANGE IMMEDIATELY!):${NC}"
    echo "   Email: admin@degensden.com"
    echo "   Password: admin123"
    echo ""
    echo -e "${CYAN}🎯 NEXT STEPS:${NC}"
    echo "   1. ✅ Test local: http://localhost:3000"
    echo "   2. 🔐 Change admin password in the app and in $APP_DIR/backend/.env"
    echo "   3. 💰 Add crypto wallet addresses to $APP_DIR/backend/.env"
    echo "   4. 🤖 Configure Discord bot token in $APP_DIR/backend/.env"
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   5. 🚀 Go live at https://$APP_DOMAIN"
    fi
    echo ""
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GOLD}🐺 Welcome to the Wolf Pack! All In. Ben Motto. 🎲${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# --- Script Execution ---
check_and_install_docker
check_and_install_cloudflared
deploy_application
