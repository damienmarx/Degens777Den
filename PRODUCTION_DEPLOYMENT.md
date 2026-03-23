# Degens777Den - Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying Degens777Den to production across Android, iOS, and Desktop platforms with optimal performance, security, and reliability.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Local Deployment](#local-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Mobile Optimization](#mobile-optimization)
7. [Performance Tuning](#performance-tuning)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Checklist

Before deploying to production, ensure the following:

- [ ] All environment variables are configured in `.env` files
- [ ] Database credentials are secure and not exposed in code
- [ ] SSL/TLS certificates are obtained (Let's Encrypt recommended)
- [ ] Wallet addresses for all supported cryptocurrencies are configured
- [ ] Discord bot token and webhook URLs are set
- [ ] CORS origins are properly configured
- [ ] Rate limiting is enabled
- [ ] Backup strategy is in place
- [ ] Monitoring and alerting are configured
- [ ] Security headers are enabled
- [ ] Database backups are automated
- [ ] Frontend build passes all tests
- [ ] Backend API endpoints are tested
- [ ] All games are functional and tested
- [ ] Mobile responsiveness is verified

---

## Environment Setup

### 1. System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB SSD
- OS: Ubuntu 20.04 LTS or later

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50 GB SSD
- OS: Ubuntu 22.04 LTS

### 2. Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt-get install -y python3 python3-pip python3-venv

# Install MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Install Docker (optional but recommended)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install PM2 for process management
sudo npm install -g pm2

# Install Nginx
sudo apt-get install -y nginx

# Install Redis (optional)
sudo apt-get install -y redis-server
```

### 3. Configure Environment Variables

**Backend (.env):**

```bash
# Database
MONGO_URL="mongodb://admin:password@localhost:27017/?authSource=admin"
DB_NAME="degensden_casino"

# Security
JWT_SECRET="your-super-secure-secret-key-here"
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Wallets
WALLET_BTC="your-btc-address"
WALLET_ETH="your-eth-address"
WALLET_LTC="your-ltc-address"
WALLET_USDC="your-usdc-address"
WALLET_USDT="your-usdt-address"

# Discord
DISCORD_BOT_TOKEN="your-discord-bot-token"
DISCORD_WEBHOOK_URL="your-webhook-url"

# Performance
WORKERS=4
DB_MAX_POOL_SIZE=100
DB_MIN_POOL_SIZE=10
```

**Frontend (.env.production):**

```bash
REACT_APP_BACKEND_URL="https://api.yourdomain.com"
REACT_APP_ENV="production"
```

---

## Local Deployment

### Using the Deploy Script

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh production

# For remote deployment
DEPLOY_HOST="your-server.com" \
DEPLOY_USER="ubuntu" \
DEPLOY_PATH="/opt/degensden" \
./deploy.sh production
```

### Manual Deployment

```bash
# 1. Build frontend
cd frontend
npm install --legacy-peer-deps --production
npm run build

# 2. Setup backend
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Create deployment directory
sudo mkdir -p /opt/degensden
sudo chown $USER:$USER /opt/degensden

# 4. Copy files
cp -r frontend/build /opt/degensden/frontend
cp -r backend /opt/degensden/

# 5. Setup environment
cp backend/.env /opt/degensden/backend/
```

---

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose up -d --build backend
```

### Deploy to Docker Hub

```bash
# Tag image
docker tag degensden-backend:latest yourusername/degensden-backend:latest

# Push to registry
docker push yourusername/degensden-backend:latest

# Pull and run on production server
docker pull yourusername/degensden-backend:latest
docker run -d --name degensden-backend \
  -e MONGO_URL="mongodb://..." \
  -p 8000:8000 \
  yourusername/degensden-backend:latest
```

---

## Cloud Deployment

### AWS Deployment

```bash
# 1. Create EC2 instance
# - Choose Ubuntu 22.04 LTS
# - Allocate 4+ GB RAM
# - Open ports 80, 443, 8000

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Run setup script
curl -fsSL https://your-domain.com/setup.sh | bash

# 4. Deploy application
cd /opt/degensden
./deploy.sh production
```

### Heroku Deployment

```bash
# 1. Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login to Heroku
heroku login

# 3. Create app
heroku create degensden

# 4. Set environment variables
heroku config:set MONGO_URL="..." JWT_SECRET="..."

# 5. Deploy
git push heroku main
```

### Vercel Deployment (Frontend only)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel --prod

# 3. Configure environment
vercel env add REACT_APP_BACKEND_URL
```

---

## Mobile Optimization

### Android Optimization

1. **Progressive Web App (PWA)**
   ```bash
   # Create manifest.json
   {
     "name": "Degens777Den",
     "short_name": "Degens",
     "start_url": "/",
     "display": "standalone",
     "background_color": "#050505",
     "theme_color": "#E0FF00"
   }
   ```

2. **Service Worker**
   ```bash
   # Enable offline functionality
   npm install workbox-cli --save-dev
   ```

3. **APK Generation**
   ```bash
   # Using Capacitor
   npm install @capacitor/core @capacitor/cli
   npx cap init
   npx cap add android
   npx cap build android
   ```

### iOS Optimization

1. **App Store Preparation**
   ```bash
   # Generate iOS app
   npx cap add ios
   npx cap build ios
   ```

2. **Sign and Deploy**
   ```bash
   # Open in Xcode
   open ios/App/App.xcworkspace
   # Configure signing and deploy
   ```

### Desktop Optimization

1. **Electron Build**
   ```bash
   npm install electron --save-dev
   npm install electron-builder --save-dev
   ```

2. **Create Executable**
   ```bash
   npm run electron-build
   ```

---

## Performance Tuning

### Frontend Optimization

```bash
# 1. Enable code splitting
npm install @loadable/component

# 2. Optimize images
npm install imagemin-cli

# 3. Analyze bundle
npm install webpack-bundle-analyzer

# 4. Enable caching
# Configure .htaccess or nginx.conf (included)
```

### Backend Optimization

```python
# 1. Enable caching
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# 2. Database indexing
db.users.create_index("email", unique=True)
db.bets.create_index("user_id")
db.bets.create_index("created_at")

# 3. Connection pooling
# Already configured in server.py
```

### Database Optimization

```bash
# 1. Enable authentication
mongo admin --eval "db.createUser({user: 'admin', pwd: 'password', roles: ['root']})"

# 2. Create indexes
mongo degensden_casino --eval "
db.users.createIndex({email: 1}, {unique: true})
db.bets.createIndex({user_id: 1})
db.bets.createIndex({created_at: -1})
"

# 3. Enable replication
# Configure replica set in production
```

---

## Monitoring & Maintenance

### Setup Monitoring

```bash
# 1. Install PM2 Plus
pm2 install pm2-auto-pull
pm2 install pm2-logrotate

# 2. Enable monitoring
pm2 monit

# 3. Setup alerts
pm2 web
# Access at http://localhost:9615
```

### Automated Backups

```bash
# Create backup script
cat > /opt/degensden/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/degensden"
mkdir -p $BACKUP_DIR
mongodump --uri="mongodb://admin:password@localhost:27017/degensden_casino" \
  --out="$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)"
EOF

# Schedule with cron
crontab -e
# Add: 0 2 * * * /opt/degensden/backup.sh
```

### Log Rotation

```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/degensden << 'EOF'
/opt/degensden/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 degensden degensden
    sharedscripts
}
EOF
```

---

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

**2. MongoDB Connection Error**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check connection
mongo --eval "db.adminCommand('ping')"
```

**3. Frontend Build Fails**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Rebuild
npm run build
```

**4. High Memory Usage**
```bash
# Check memory
free -h

# Monitor processes
top

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Rollback Procedures

### Automatic Rollback

```bash
# Using deploy script
./deploy.sh rollback
```

### Manual Rollback

```bash
# 1. Stop services
pm2 stop degensden-backend
sudo systemctl stop nginx

# 2. Restore from backup
cp -r /backups/degensden/previous_deployment /opt/degensden

# 3. Restart services
pm2 start degensden-backend
sudo systemctl start nginx

# 4. Verify
curl http://localhost:8000/api/health
```

---

## Security Checklist

- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Setup DDoS protection (Cloudflare recommended)
- [ ] Enable 2FA for admin accounts
- [ ] Rotate API keys regularly
- [ ] Monitor for suspicious activity
- [ ] Keep dependencies updated
- [ ] Regular security audits
- [ ] Backup encryption enabled

---

## Support & Troubleshooting

For issues or questions:
1. Check logs: `pm2 logs degensden-backend`
2. Review documentation in `/docs`
3. Contact support team

---

## Version History

- **v1.0.0** - Initial production release
  - All games functional
  - Cross-platform support
  - Responsive design
  - Production-ready deployment

---

**Last Updated:** March 23, 2026
**Maintained By:** Degens777Den Team
