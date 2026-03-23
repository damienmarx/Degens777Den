# ENVIRONMENT VARIABLES - Complete Setup Guide

## 📋 Overview

This guide covers ALL environment variables required for Degens777Den production deployment.

---

## 🔧 Backend Environment (.env)

Location: `/app/backend/.env`

```env
# ==================== DATABASE ====================
# MongoDB connection with authentication
MONGO_URL="mongodb://admin:monalisa@localhost:27017/?authSource=admin"
DB_NAME="degensden_casino"

# ==================== SECURITY ====================
# JWT secret for authentication tokens (CHANGE THIS IN PRODUCTION!)
JWT_SECRET="degens777den-ultra-secure-secret-7D7D7-2025-CHANGE-ME"

# CORS origins (comma-separated for multiple domains)
CORS_ORIGINS="https://cloutscape.org,https://www.cloutscape.org"

# ==================== CRYPTO WALLETS ====================
# Your cryptocurrency deposit addresses
# ⚠️ CRITICAL: Use YOUR addresses, not placeholders!

WALLET_BTC="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
WALLET_ETH="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
WALLET_LTC="ltc1qw508d6qejxtdg4y5r3zarvary0c5xw7kgmn4n9"
WALLET_USDC="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
WALLET_USDT="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

# ==================== OSRS GOLD ====================
# OSRS deposit RSN (RuneScape Name)
OSRS_DEPOSIT_RSN="KodakGP"

# OSRS GP limits (in GP, not millions)
OSRS_MIN_DEPOSIT=15000000    # 15M GP
OSRS_MAX_DEPOSIT=750000000   # 750M GP

# ==================== DEPOSIT/WITHDRAWAL LIMITS ====================
# BTC limits (in USD equivalent)
BTC_MIN_DEPOSIT_USD=5
BTC_MAX_DEPOSIT_USD=250

# Daily withdrawal limit per user (USD)
DAILY_WITHDRAW_LIMIT_USD=500

# VIP withdrawal limits (optional, overrides above for VIP)
VIP_DAILY_WITHDRAW_LIMIT_USD=5000

# ==================== DISCORD INTEGRATION ====================
# Discord bot token (from https://discord.com/developers/applications)
DISCORD_BOT_TOKEN=""

# Discord webhook URL for notifications
DISCORD_WEBHOOK_URL=""

# Discord OAuth2 credentials (optional)
DISCORD_CLIENT_ID=""
DISCORD_CLIENT_SECRET=""
DISCORD_REDIRECT_URI="https://cloutscape.org/auth/discord/callback"

# ==================== KODAKGP INTEGRATION ====================
# KodakGP API settings
KODAKGP_API_ENABLED=true
KODAKGP_CONTACT_DISCORD="KodakGP#0000"

# KodakGP gold rates (USD per 1M GP)
KODAKGP_BUY_RATE=0.45
KODAKGP_SELL_RATE=0.50

# ==================== VIP SYSTEM ====================
# VIP tier thresholds (total wagered in USD)
VIP_BRONZE_MIN=100
VIP_SILVER_MIN=1000
VIP_GOLD_MIN=10000
VIP_PLATINUM_MIN=50000
VIP_DRAGON_MIN=250000

# VIP benefits (percentages)
VIP_BRONZE_RAKEBACK=1.0
VIP_SILVER_RAKEBACK=2.5
VIP_GOLD_RAKEBACK=5.0
VIP_PLATINUM_RAKEBACK=10.0
VIP_DRAGON_RAKEBACK=15.0

VIP_BRONZE_LOSSBACK=0.5
VIP_SILVER_LOSSBACK=1.0
VIP_GOLD_LOSSBACK=2.5
VIP_PLATINUM_LOSSBACK=5.0
VIP_DRAGON_LOSSBACK=10.0

# ==================== GAME SETTINGS ====================
# House edge for each game (percentage)
DICE_HOUSE_EDGE=3.0
KENO_HOUSE_EDGE=3.0
CRASH_HOUSE_EDGE=3.0
WHEEL_HOUSE_EDGE=3.0
PLINKO_HOUSE_EDGE=3.0
LIMBO_HOUSE_EDGE=3.0

# RTP (Return to Player) - should be 100 - house_edge
# For transparency: 97% RTP = 3% house edge
GLOBAL_RTP=97.0

# ==================== RATE LIMITING ====================
# Max concurrent players
MAX_CONCURRENT_PLAYERS=350

# Rate limits (requests per minute)
LOGIN_RATE_LIMIT=5
BET_RATE_LIMIT=120
CHAT_RATE_LIMIT=20
WITHDRAW_RATE_LIMIT=3

# ==================== EMAIL (OPTIONAL) ====================
# For notifications and password resets
SMTP_HOST="smtp.sendgrid.net"
SMTP_PORT=587
SMTP_USER=""
SMTP_PASSWORD=""
FROM_EMAIL="noreply@cloutscape.org"

# ==================== CLOUDFLARE ====================
# Cloudflare tunnel name
TUNNEL_NAME="kodakclout-prod"

# Cloudflare API credentials (optional, for automatic DNS)
CLOUDFLARE_API_TOKEN=""
CLOUDFLARE_ZONE_ID=""

# ==================== ADMIN ====================
# Admin credentials (created on first seed)
ADMIN_EMAIL="admin@degensden.com"
ADMIN_PASSWORD="admin123"  # ⚠️ CHANGE IN PRODUCTION!
ADMIN_USERNAME="DegenGod"

# ==================== FEATURES ====================
# Feature flags
ENABLE_CHAT=true
ENABLE_TIPS=true
ENABLE_RAIN=true
ENABLE_REFERRALS=true
ENABLE_VIP_SYSTEM=true
ENABLE_DISCORD_OAUTH=false  # Set to true when Discord OAuth configured

# Referral bonus amounts
REFERRAL_BONUS_USD=5
REFERRAL_BONUS_OSRS_GP=35000000  # 35M GP

# ==================== LOGGING ====================
# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL="INFO"

# Log to file
LOG_FILE="/var/log/degensden/backend.log"

# ==================== PERFORMANCE ====================
# Uvicorn workers (1 per CPU core recommended)
WORKERS=4

# WebSocket ping interval (seconds)
WS_PING_INTERVAL=30

# Database connection pool
DB_MAX_POOL_SIZE=100
DB_MIN_POOL_SIZE=10

# ==================== SECURITY ====================
# Session timeout (seconds)
SESSION_TIMEOUT=3600

# Token expiration (seconds)
ACCESS_TOKEN_EXPIRE=86400  # 24 hours
REFRESH_TOKEN_EXPIRE=604800  # 7 days

# Password requirements
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=true
REQUIRE_NUMBERS=true
REQUIRE_SPECIAL_CHARS=false

# ==================== TESTING ====================
# Set to true for development/testing
DEBUG_MODE=false
SKIP_EMAIL_VERIFICATION=true
ALLOW_TEST_DEPOSITS=false
```

---

## 🎨 Frontend Environment (.env)

Location: `/app/frontend/.env`

```env
# Backend API URL
# ⚠️ MUST match your domain/tunnel
REACT_APP_BACKEND_URL=https://cloutscape.org

# WebSocket configuration
# Hot reload settings (production should use 443)
WDS_SOCKET_PORT=443

# Health check (disable in production)
ENABLE_HEALTH_CHECK=false

# Feature flags (matches backend)
REACT_APP_ENABLE_DISCORD_LOGIN=false
REACT_APP_MAX_PLAYERS=350

# Analytics (optional)
REACT_APP_GA_TRACKING_ID=""
REACT_APP_HOTJAR_ID=""

# Branding
REACT_APP_SITE_NAME="Degens777Den"
REACT_APP_SITE_DOMAIN="cloutscape.org"
REACT_APP_SUPPORT_EMAIL="support@cloutscape.org"

# Social links
REACT_APP_DISCORD_INVITE=""
REACT_APP_TWITTER_HANDLE=""
REACT_APP_TELEGRAM_LINK=""
```

---

## 🔐 Sensitive Variables Checklist

### ⚠️ MUST CHANGE IN PRODUCTION:

- [ ] `JWT_SECRET` - Generate strong random string
- [ ] `ADMIN_PASSWORD` - Use strong password
- [ ] `WALLET_BTC` - Your Bitcoin address
- [ ] `WALLET_ETH` - Your Ethereum address  
- [ ] `WALLET_LTC` - Your Litecoin address
- [ ] `WALLET_USDC` - Your USDC address
- [ ] `WALLET_USDT` - Your Tether address

### 🔧 CONFIGURE IF USING:

- [ ] `DISCORD_BOT_TOKEN` - If using Discord bot
- [ ] `DISCORD_WEBHOOK_URL` - For notifications
- [ ] `DISCORD_CLIENT_ID` - For Discord OAuth
- [ ] `DISCORD_CLIENT_SECRET` - For Discord OAuth
- [ ] `SMTP_USER` / `SMTP_PASSWORD` - If using email
- [ ] `CLOUDFLARE_API_TOKEN` - For automatic DNS

---

## 🚀 Quick Setup Commands

### Generate Strong JWT Secret:
```bash
openssl rand -hex 32
```

### Generate Admin Password:
```bash
openssl rand -base64 24
```

### Test MongoDB Connection:
```bash
mongosh "mongodb://admin:monalisa@localhost:27017/?authSource=admin"
```

### Validate Environment:
```bash
cd /app/backend
source venv/bin/activate
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('JWT_SECRET' in os.environ)"
```

---

## 📊 Environment Validation Script

Create `/app/scripts/validate_env.sh`:

```bash
#!/bin/bash

echo "🔍 Validating environment variables..."

REQUIRED_VARS=(
  "MONGO_URL"
  "JWT_SECRET"
  "WALLET_BTC"
  "WALLET_ETH"
  "OSRS_DEPOSIT_RSN"
)

MISSING=0

for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    echo "❌ Missing: $VAR"
    MISSING=$((MISSING + 1))
  else
    echo "✅ Found: $VAR"
  fi
done

if [ $MISSING -gt 0 ]; then
  echo ""
  echo "⚠️  $MISSING required variables missing!"
  echo "Edit /app/backend/.env before deployment."
  exit 1
else
  echo ""
  echo "✅ All required variables present!"
fi
```

---

## 🎯 Production Checklist

Before deploying:

1. **Security**:
   - [ ] Change `JWT_SECRET`
   - [ ] Change `ADMIN_PASSWORD`
   - [ ] Set strong `MONGO_URL` password
   - [ ] Verify `CORS_ORIGINS` matches domain

2. **Wallets**:
   - [ ] Verify all wallet addresses
   - [ ] Test deposits to each address
   - [ ] Confirm you control private keys

3. **Limits**:
   - [ ] Set appropriate deposit limits
   - [ ] Configure withdrawal limits
   - [ ] Verify `MAX_CONCURRENT_PLAYERS=350`

4. **Integrations**:
   - [ ] Configure Discord if using
   - [ ] Setup KodakGP contact info
   - [ ] Test SMTP if using email

5. **Features**:
   - [ ] Disable `DEBUG_MODE`
   - [ ] Set `LOG_LEVEL=INFO`
   - [ ] Enable/disable optional features

---

## 📞 Support

Questions about environment setup?

- 📧 Email: support@cloutscape.org
- 💬 Discord: [Discord Link]
- 📖 Docs: See `/app/DEPLOYMENT_GUIDE.md`

---

**© 2025 Degens777Den**
