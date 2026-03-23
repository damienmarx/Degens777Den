# Degens777Den - Phase 1 Complete! 🎰

## ✅ What's Included

### Casino Games (6 Working Games)
1. **Dice** - Classic dice with customizable odds and auto-bet
2. **Keno** - Pick 1-10 numbers from 40, RuneScape-style payouts
3. **Crash** - Ride the rocket, cash out before it crashes
4. **Lucky Wheel** - Spin for 0x to 21x multipliers
5. **Plinko** - Drop the ball through 16 rows of pegs
6. **Limbo** - Set your target multiplier, beat the RNG

### KodakGP Integration ✨
- **Buy Gold** - Purchase OSRS GP with crypto/PayPal
- **Sell Gold** - Sell your OSRS GP for real money
- **OSRS Services** - Pure accounts, quests, leveling, fire cape, infernal, diaries
- **Order Tracking** - View all your gold orders and service requests

### Core Features
- ✅ Provably Fair system (verifiable game results)
- ✅ Wallet (BTC, ETH, LTC, USDC, USDT, OSRS GP)
- ✅ VIP Program (5 tiers: Bronze → Dragon)
- ✅ Referral System ("Refer a Degen" - $5 or 35M GP bonus)
- ✅ Live Chat (with tips and rain features)
- ✅ Leaderboard
- ✅ Admin Dashboard
- ✅ Discord Bot (server setup, notifications, commands)

---

## 🚀 Deployment Instructions

### Option 1: Automated Production Setup (Recommended)

Run the all-in-one setup script on your Ubuntu server:

```bash
cd /app
sudo bash setup-production.sh
```

This script will:
- Install Node.js, Python, MongoDB, Nginx, Supervisor
- Configure MongoDB with authentication (password: monalisa)
- Setup backend and frontend
- Configure services to auto-start
- Prepare for Cloudflare tunnel

### Option 2: Manual Setup

#### 1. Install Dependencies

```bash
# Backend
cd /app/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd /app/frontend
yarn install
yarn build
```

#### 2. Configure MongoDB

```bash
# Start MongoDB
sudo systemctl start mongod

# Create admin user
mongosh
> use admin
> db.createUser({user: "admin", pwd: "monalisa", roles: ["root"]})
> exit

# Enable authentication in /etc/mongod.conf
security:
  authorization: enabled

sudo systemctl restart mongod
```

#### 3. Start Services

```bash
# Backend (port 8001)
cd /app/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 &

# Frontend (port 3000)
cd /app/frontend
npx serve -s build -l 3000 &
```

#### 4. Seed Database

```bash
curl -X POST http://localhost:8001/api/seed
```

This creates an admin user:
- Email: admin@degensden.com
- Password: admin123

---

## 🌐 Cloudflare Tunnel Setup

### Step 1: Login to Cloudflare
```bash
cloudflared tunnel login
```

### Step 2: Create Tunnel
```bash
cloudflared tunnel create kodakclout-prod
```

### Step 3: Configure DNS
```bash
cloudflared tunnel route dns kodakclout-prod cloutscape.org
```

### Step 4: Create Config File

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /root/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: cloutscape.org
    service: http://localhost:80
  - hostname: www.cloutscape.org
    service: http://localhost:80
  - service: http_status:404
```

### Step 5: Start Tunnel
```bash
# Test run
cloudflared tunnel run kodakclout-prod

# Install as system service
cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

---

## ⚙️ Configuration

### Backend Environment (`/app/backend/.env`)

```env
MONGO_URL="mongodb://admin:monalisa@localhost:27017/?authSource=admin"
DB_NAME="degensden_casino"
JWT_SECRET="degens777den-ultra-secure-secret-7D7D7-2025"

# Add your crypto wallet addresses
WALLET_BTC="your-btc-address"
WALLET_ETH="your-eth-address"
# etc...

# OSRS Configuration
OSRS_DEPOSIT_RSN="KodakGP"

# Discord (optional)
DISCORD_BOT_TOKEN="your-bot-token"
DISCORD_WEBHOOK_URL="your-webhook-url"
```

### Frontend Environment (`/app/frontend/.env`)

```env
REACT_APP_BACKEND_URL=https://cloutscape.org
```

---

## 🎮 Admin Access

After seeding the database:
- Email: `admin@degensden.com`
- Password: `admin123`

**IMPORTANT**: Change this password immediately in production!

---

## 📊 Service Management

### Using Supervisor (Production)

```bash
# View status
sudo supervisorctl status

# Restart backend
sudo supervisorctl restart degensden-backend

# Restart frontend
sudo supervisorctl restart degensden-frontend

# View logs
sudo tail -f /var/log/supervisor/degensden-backend.out.log
sudo tail -f /var/log/supervisor/degensden-backend.err.log
```

### Manual Control

```bash
# Stop all
pkill -f uvicorn
pkill -f serve

# Start backend
cd /app/backend && source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 &

# Start frontend
cd /app/frontend
npx serve -s build -l 3000 &
```

---

## 🧪 Testing

### Local Testing

```bash
# Test backend API
curl http://localhost:8001/api/

# Test KodakGP rates
curl http://localhost:8001/api/kodakgp/rates

# Access frontend
open http://localhost:3000
```

### Production Testing

```bash
# After Cloudflare setup
curl https://cloutscape.org/api/

# Visit site
open https://cloutscape.org
```

---

## 📝 Database Info

- **URL**: `mongodb://admin:monalisa@localhost:27017/?authSource=admin`
- **Database**: `degensden_casino`
- **Collections**:
  - `users` - User accounts
  - `wallets` - User balances
  - `bets` - Game history
  - `seeds` - Provably fair seeds
  - `promo_codes` - Referral codes
  - `transactions` - Deposits/withdrawals
  - `kodakgp_orders` - Gold orders
  - `kodakgp_services` - Service requests
  - `forum_posts` - Community posts

---

## 🎨 Branding

- **Name**: Degens777Den
- **Logo**: 7 D7D 7 (in gold/neon style)
- **Domain**: cloutscape.org
- **Theme**: Black/Gold/Chrome/Obsidian ("Underground Degen VIP")
- **Colors**:
  - Primary: #E0FF00 (Electric Neon)
  - Win: #00FFA3
  - Loss: #FF2346
  - OSRS Gold: #FFC800

---

## 🔐 Security Checklist

Before going live:

1. ✅ Change admin password
2. ✅ Set strong JWT_SECRET in .env
3. ✅ Configure real crypto wallet addresses
4. ✅ Setup Discord webhooks for notifications
5. ✅ Enable HTTPS via Cloudflare
6. ✅ Setup firewall rules (UFW)
7. ✅ Configure MongoDB authentication
8. ✅ Regular backups of MongoDB
9. ✅ Monitor logs for suspicious activity
10. ✅ Rate limiting on API endpoints

---

## 📞 Support

**KodakGP Contact**: Discord - KodakGP (update in backend/.env)

**Casino Issues**:
- Check logs: `/var/log/supervisor/`
- Check MongoDB: `mongosh mongodb://admin:monalisa@localhost:27017`
- Check services: `sudo supervisorctl status`

---

## 🚧 What's Next? (Phase 2)

Phase 1 is complete! Here's what can be added next:

1. **New Games**:
   - Mines (minesweeper-style)
   - Degen Slots (RuneScape-inspired with reels, multipliers, bonus rounds)
   - Omaha Poker (hourly tournaments with 10M GP prize)

2. **Enhanced Features**:
   - Privacy toggles (hide username)
   - Real-time game history tracking
   - Discord OAuth login
   - Community forum/blog
   - User dashboard with POPs/vouchers

3. **Advanced**:
   - Mobile app
   - Affiliate tracking dashboard
   - Automated GP trading via bot
   - Live streaming integration

---

## ✅ Phase 1 Completion Summary

**What Works:**
- ✅ 6 casino games (fully functional, provably fair)
- ✅ KodakGP buy/sell gold interface
- ✅ OSRS services request system
- ✅ Wallet management (all currencies)
- ✅ VIP system with rakeback/lossback
- ✅ Referral system with bonuses
- ✅ Live chat with tips/rain
- ✅ Admin dashboard
- ✅ Production-ready deployment script
- ✅ MongoDB with authentication
- ✅ Cloudflare tunnel support

**Deployment Status:**
- Backend: ✅ Ready
- Frontend: ✅ Ready
- Database: ✅ Configured
- Tunnel Setup: ⚠️ Manual step required (see Cloudflare section)

---

**You're ready to launch! 🚀**
