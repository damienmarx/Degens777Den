#!/bin/bash

################################################################################
# DEGENS777DEN - ALL-IN-ONE PRODUCTION DEPLOY SCRIPT
# Handles frontend build, backend setup, and deployment to production
################################################################################

set -e

# ==================== COLORS FOR OUTPUT ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== LOGGING FUNCTIONS ====================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ==================== CONFIGURATION ====================
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
BACKEND_DIR="${PROJECT_DIR}/backend"
BUILD_DIR="${PROJECT_DIR}/build"
DEPLOY_LOG="${PROJECT_DIR}/deploy.log"

# Environment
ENVIRONMENT="${1:-production}"
DEPLOY_HOST="${DEPLOY_HOST:-}"
DEPLOY_USER="${DEPLOY_USER:-}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/degensden}"

# Timestamps
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${PROJECT_DIR}/backups/${TIMESTAMP}"

# ==================== PRE-DEPLOYMENT CHECKS ====================
check_requirements() {
    log_info "Checking system requirements..."

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    log_success "Node.js $(node --version) found"

    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    log_success "npm $(npm --version) found"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    log_success "Python $(python3 --version) found"

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed"
        exit 1
    fi
    log_success "pip3 found"

    # Check git
    if ! command -v git &> /dev/null; then
        log_error "git is not installed"
        exit 1
    fi
    log_success "git $(git --version | awk '{print $3}') found"
}

# ==================== ENVIRONMENT SETUP ====================
setup_environment() {
    log_info "Setting up environment for ${ENVIRONMENT}..."

    # Create build directory
    mkdir -p "${BUILD_DIR}"
    mkdir -p "${BACKUP_DIR}"

    # Check for required env files
    if [ ! -f "${BACKEND_DIR}/.env" ]; then
        log_error "Backend .env file not found at ${BACKEND_DIR}/.env"
        exit 1
    fi

    if [ ! -f "${FRONTEND_DIR}/.env" ]; then
        log_error "Frontend .env file not found at ${FRONTEND_DIR}/.env"
        exit 1
    fi

    log_success "Environment files found"
}

# ==================== FRONTEND BUILD ====================
build_frontend() {
    log_info "Building frontend..."

    cd "${FRONTEND_DIR}"

    # Install dependencies
    log_info "Installing frontend dependencies..."
    npm install --legacy-peer-deps --production

    # Build production bundle
    log_info "Creating production build..."
    npm run build

    # Verify build output
    if [ ! -d "${FRONTEND_DIR}/build" ]; then
        log_error "Frontend build failed - build directory not created"
        exit 1
    fi

    # Get build size
    BUILD_SIZE=$(du -sh "${FRONTEND_DIR}/build" | cut -f1)
    log_success "Frontend built successfully (${BUILD_SIZE})"

    # Copy to deployment directory
    cp -r "${FRONTEND_DIR}/build" "${BUILD_DIR}/frontend"
    log_success "Frontend build copied to deployment directory"
}

# ==================== BACKEND SETUP ====================
setup_backend() {
    log_info "Setting up backend..."

    cd "${BACKEND_DIR}"

    # Create Python virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install Python dependencies
    log_info "Installing backend dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

    log_success "Backend dependencies installed"
}

# ==================== CLEANUP ====================
cleanup_build() {
    log_info "Cleaning up unnecessary files..."

    # Remove backup CSS file
    rm -f "${FRONTEND_DIR}/src/App.css.backup"

    # Remove node_modules from build
    rm -rf "${BUILD_DIR}/frontend/node_modules"

    # Remove source maps in production
    find "${BUILD_DIR}/frontend" -name "*.map" -delete

    # Remove test files
    find "${BUILD_DIR}" -name "*.test.js" -delete
    find "${BUILD_DIR}" -name "*.spec.js" -delete

    log_success "Cleanup completed"
}

# ==================== OPTIMIZATION ====================
optimize_build() {
    log_info "Optimizing build for production..."

    # Gzip static assets
    log_info "Compressing static assets..."
    cd "${BUILD_DIR}/frontend"

    find . -type f \( -name "*.js" -o -name "*.css" -o -name "*.html" \) -exec gzip -9 -k {} \;

    # Create .htaccess for gzip serving (if using Apache)
    cat > ".htaccess" << 'EOF'
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>

<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule ^ index.html [QSA,L]
</IfModule>

# Cache control headers
<FilesMatch "\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$">
  Header set Cache-Control "max-age=31536000, public"
</FilesMatch>

<FilesMatch "\.html$">
  Header set Cache-Control "max-age=3600, public"
</FilesMatch>
EOF

    log_success "Build optimized"
}

# ==================== HEALTH CHECKS ====================
health_check() {
    log_info "Running health checks..."

    # Check frontend build
    if [ ! -f "${BUILD_DIR}/frontend/index.html" ]; then
        log_error "Frontend build missing index.html"
        exit 1
    fi

    # Check backend files
    if [ ! -f "${BACKEND_DIR}/server.py" ]; then
        log_error "Backend server.py not found"
        exit 1
    fi

    # Verify key dependencies
    cd "${BACKEND_DIR}"
    source venv/bin/activate

    python3 -c "import fastapi; import motor; import pymongo; import jwt; import bcrypt" 2>/dev/null || {
        log_error "Backend dependencies verification failed"
        exit 1
    }

    log_success "Health checks passed"
}

# ==================== BACKUP ====================
create_backup() {
    log_info "Creating backup of current deployment..."

    if [ -d "${DEPLOY_PATH}" ]; then
        cp -r "${DEPLOY_PATH}" "${BACKUP_DIR}/previous_deployment"
        log_success "Backup created at ${BACKUP_DIR}/previous_deployment"
    fi
}

# ==================== DEPLOYMENT ====================
deploy_local() {
    log_info "Deploying to local system..."

    # Create deployment directory
    mkdir -p "${DEPLOY_PATH}"

    # Copy frontend build
    log_info "Deploying frontend..."
    rm -rf "${DEPLOY_PATH}/frontend" || true
    cp -r "${BUILD_DIR}/frontend" "${DEPLOY_PATH}/"

    # Copy backend
    log_info "Deploying backend..."
    rm -rf "${DEPLOY_PATH}/backend" || true
    cp -r "${BACKEND_DIR}" "${DEPLOY_PATH}/"

    # Copy environment files
    cp "${BACKEND_DIR}/.env" "${DEPLOY_PATH}/backend/"
    cp "${BACKEND_DIR}/.env.production" "${DEPLOY_PATH}/backend/" 2>/dev/null || true

    log_success "Local deployment completed"
}

deploy_remote() {
    log_info "Deploying to remote server..."

    if [ -z "${DEPLOY_HOST}" ] || [ -z "${DEPLOY_USER}" ]; then
        log_error "DEPLOY_HOST and DEPLOY_USER must be set for remote deployment"
        exit 1
    fi

    # Create deployment archive
    log_info "Creating deployment archive..."
    cd "${BUILD_DIR}"
    tar -czf "degensden-${TIMESTAMP}.tar.gz" frontend backend

    # Upload to remote server
    log_info "Uploading to ${DEPLOY_USER}@${DEPLOY_HOST}..."
    scp "degensden-${TIMESTAMP}.tar.gz" "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/"

    # Extract on remote server
    log_info "Extracting on remote server..."
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "cd ${DEPLOY_PATH} && tar -xzf degensden-${TIMESTAMP}.tar.gz && rm degensden-${TIMESTAMP}.tar.gz"

    # Cleanup local archive
    rm "degensden-${TIMESTAMP}.tar.gz"

    log_success "Remote deployment completed"
}

# ==================== SERVICE MANAGEMENT ====================
start_services() {
    log_info "Starting services..."

    # Start backend with PM2 (if available)
    if command -v pm2 &> /dev/null; then
        log_info "Starting backend with PM2..."
        cd "${DEPLOY_PATH}/backend"
        pm2 start server.py --name degensden-backend --interpreter python3
        pm2 save
        pm2 startup
    else
        log_warning "PM2 not found - backend must be started manually"
    fi

    # Start frontend with serve (if available)
    if command -v serve &> /dev/null; then
        log_info "Starting frontend with serve..."
        cd "${DEPLOY_PATH}/frontend"
        serve -s . -l 3000 &
    else
        log_warning "serve not found - frontend must be served with your web server"
    fi

    log_success "Services started"
}

# ==================== VERIFICATION ====================
verify_deployment() {
    log_info "Verifying deployment..."

    # Check if files exist
    if [ ! -d "${DEPLOY_PATH}/frontend" ]; then
        log_error "Frontend deployment verification failed"
        exit 1
    fi

    if [ ! -d "${DEPLOY_PATH}/backend" ]; then
        log_error "Backend deployment verification failed"
        exit 1
    fi

    # Check file permissions
    if [ ! -x "${DEPLOY_PATH}/backend/server.py" ]; then
        chmod +x "${DEPLOY_PATH}/backend/server.py"
    fi

    log_success "Deployment verification passed"
}

# ==================== ROLLBACK ====================
rollback() {
    log_warning "Rolling back deployment..."

    if [ -d "${BACKUP_DIR}/previous_deployment" ]; then
        rm -rf "${DEPLOY_PATH}"
        cp -r "${BACKUP_DIR}/previous_deployment" "${DEPLOY_PATH}"
        log_success "Rollback completed"
    else
        log_error "No previous deployment backup found"
        exit 1
    fi
}

# ==================== MAIN EXECUTION ====================
main() {
    log_info "Starting Degens777Den deployment process..."
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Project directory: ${PROJECT_DIR}"
    log_info "Deployment path: ${DEPLOY_PATH}"

    # Trap errors
    trap 'log_error "Deployment failed"; exit 1' ERR

    # Execute deployment steps
    check_requirements
    setup_environment
    build_frontend
    setup_backend
    cleanup_build
    optimize_build
    health_check
    create_backup
    
    if [ -z "${DEPLOY_HOST}" ]; then
        deploy_local
    else
        deploy_remote
    fi

    verify_deployment
    start_services

    log_success "Deployment completed successfully!"
    log_info "Deployment log: ${DEPLOY_LOG}"

    # Create summary
    cat > "${DEPLOY_LOG}" << EOF
Deployment Summary
==================
Timestamp: ${TIMESTAMP}
Environment: ${ENVIRONMENT}
Project: ${PROJECT_DIR}
Deployment Path: ${DEPLOY_PATH}
Frontend Build: ${BUILD_DIR}/frontend
Backend Path: ${DEPLOY_PATH}/backend
Status: SUCCESS

Next Steps:
1. Verify the application is running
2. Check logs for any warnings
3. Test all game functionality
4. Verify responsive design on mobile devices
5. Monitor performance metrics

Rollback Command:
./deploy.sh rollback

EOF

    cat "${DEPLOY_LOG}"
}

# ==================== ARGUMENT HANDLING ====================
case "${1:-}" in
    rollback)
        rollback
        ;;
    *)
        main
        ;;
esac
