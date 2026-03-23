# Degens777Den Casino Platform

**Domain**: [cloutscape.org](https://cloutscape.org)  
**Casino**: Degens777Den (7 D7D 7)  
**Theme**: Obsidian Luxury • Gold Lining • Dark Provocative  
**Max Capacity**: 350 concurrent players  

---

## 🎰 What is Degens777Den?

A **100% transparent, provably fair** casino platform for OSRS degens and crypto gamblers who demand:
- ✅ **Real 97% RTP** (not manipulated)
- ✅ **Verifiable RNG** (every seed public)
- ✅ **No predatory tactics** (anti-scam, anti-exploitation)
- ✅ **VIP rewards** (up to 15% rakeback + 10% lossback)
- ✅ **OSRS Gold integration** (via KodakGP partnership)

**"In a world of sheep, be a degen."** 🐺

---

## 🎮 Features

### Casino Games (6)
1. **Dice** - Classic provably fair dice
2. **Keno** - Pick 1-10 numbers, RuneScape-style payouts
3. **Crash** - Ride the rocket, cash out before crash
4. **Lucky Wheel** - Spin for 0× to 21× multipliers
5. **Plinko** - Drop the ball through 16 rows
6. **Limbo** - Set your target, beat the RNG

### Core Systems
- 💰 **Multi-Currency Wallet**: BTC, ETH, LTC, USDC, USDT, OSRS GP
- 👑 **5-Tier VIP System**: Bronze → Silver → Gold → Platinum → **DRAGON**
- 🎁 **Referral Program**: $5 USD or 35M GP per referral
- 💬 **Live Chat**: Tips, rain, community
- 🏆 **Leaderboard**: Top wagerers
- 🛡️ **Provably Fair**: 100% transparent, verifiable seeds

### KodakGP Integration
- Buy OSRS Gold (as low as $0.45/M)
- Sell OSRS Gold for crypto/PayPal
- Pure accounts & services (quests, capes, leveling)
- Community forum/blog

---

## 🎨 Design Philosophy

**"Obsidian Luxury"** - Dark, mysterious, exclusive.

- **Obsidian Black** (#0A0A0F) - Deep void
- **Gold Lining** (#D4AF37) - Wealth & status
- **Red Accents** (#DC143C) - Power & danger
- **Glassmorphism** - Backdrop blur with gold borders
- **Gold Coin Rain** - Triggers on rain events (100 coins)

**Target Audience**: High-stakes gamblers, OSRS whales, VIP members who demand exclusivity.

---

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04+ server
- 2GB+ RAM
- MongoDB
- Node.js 20+
- Python 3.11+
- Cloudflare account (for tunnel)

### One-Command Deployment

```bash
git clone https://github.com/damienmarx/Degens777Den.git
cd Degens777Den
sudo bash setup-production.sh
```

**Follow the prompts for:**
1. MongoDB setup (password: monalisa)
2. Cloudflare tunnel configuration
3. Environment variables
4. Service startup

---

## 📖 Documentation

Essential reading:

1. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Full deployment walkthrough
2. **[ENV_VARIABLES_GUIDE.md](ENV_VARIABLES_GUIDE.md)** - All environment variables explained
3. **[TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)** - Legal terms, user conduct
4. **[WHY_DEGENS777DEN.md](WHY_DEGENS777DEN.md)** - Brand manifesto, proof of concept
5. **[THEME_ENHANCEMENTS.md](THEME_ENHANCEMENTS.md)** - UI/UX design system

---

## ⚙️ Configuration

### Backend Environment

```bash
# Edit environment variables
nano /app/backend/.env
```

**Critical variables**:
- `MONGO_URL` - MongoDB connection with auth
- `JWT_SECRET` - Strong random string
- `WALLET_BTC`, `WALLET_ETH`, etc. - Your crypto addresses
- `OSRS_DEPOSIT_RSN` - OSRS deposit account

See [ENV_VARIABLES_GUIDE.md](ENV_VARIABLES_GUIDE.md) for full list.

### Frontend Environment

```bash
nano /app/frontend/.env
```

**Key variables**:
- `REACT_APP_BACKEND_URL` - Your domain (https://cloutscape.org)

---

## 🌐 Cloudflare Tunnel Setup

**Domain**: cloutscape.org  
**Tunnel**: kodakclout-prod  

```bash
# 1. Login to Cloudflare
cloudflared tunnel login

# 2. Create tunnel
cloudflared tunnel create kodakclout-prod

# 3. Route DNS
cloudflared tunnel route dns kodakclout-prod cloutscape.org

# 4. Create config
nano ~/.cloudflared/config.yml
```

**config.yml**:
```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /root/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: cloutscape.org
    service: http://localhost:80
  - service: http_status:404
```

```bash
# 5. Start tunnel
cloudflared service install
sudo systemctl start cloudflared
```

---

## 🔐 Security Checklist

Before going live:

- [ ] Change `JWT_SECRET` to random 32-byte string
- [ ] Change `ADMIN_PASSWORD` from default
- [ ] Verify all wallet addresses are YOURS
- [ ] Set `CORS_ORIGINS` to your domain only
- [ ] Enable firewall (UFW)
- [ ] Setup MongoDB authentication
- [ ] Configure backups
- [ ] Test deposits on testnet first
- [ ] Review [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)

---

## 👤 Default Admin

After seeding database:
- **Email**: admin@degensden.com
- **Password**: admin123

**⚠️ CHANGE IMMEDIATELY IN PRODUCTION!**

---

## 🎮 Testing

### Local Development

```bash
cd /app
bash start-local.sh
```

Access: http://localhost:3000

### Production

After Cloudflare setup:
- Website: https://cloutscape.org
- API: https://cloutscape.org/api
- WebSocket: wss://cloutscape.org/ws

---

## 📊 Monitoring

### Service Status

```bash
sudo supervisorctl status
```

### View Logs

```bash
# Backend
tail -f /var/log/supervisor/degensden-backend.out.log
tail -f /var/log/supervisor/degensden-backend.err.log

# Frontend
tail -f /var/log/supervisor/degensden-frontend.out.log
```

### MongoDB

```bash
mongosh "mongodb://admin:monalisa@localhost:27017/?authSource=admin"

# Check collections
use degensden_casino
show collections
db.users.countDocuments()
db.bets.countDocuments()
```

---

## 🏗️ Project Structure

```
/app/
├── backend/              # FastAPI backend
│   ├── server.py         # Main API + game logic
│   ├── discord_bot.py    # Discord server bot
│   ├── requirements.txt  # Python dependencies
│   └── .env              # Environment variables
├── frontend/             # React frontend
│   ├── src/
│   │   ├── App.js        # Main component (2900+ lines)
│   │   ├── App.css       # Component styles
│   │   └── index.css     # Global theme (obsidian luxury)
│   ├── public/
│   │   ├── logo-primary.svg
│   │   ├── logo-compact.svg
│   │   └── logo-wordmark.svg
│   ├── package.json
│   └── .env
├── setup-production.sh   # One-click deployment
├── start-local.sh        # Local testing
└── [DOCUMENTATION]
    ├── DEPLOYMENT_GUIDE.md
    ├── ENV_VARIABLES_GUIDE.md
    ├── TERMS_OF_SERVICE.md
    ├── WHY_DEGENS777DEN.md
    └── THEME_ENHANCEMENTS.md
```

---

## 🤝 Support

**Degens777Den Team**
- 📧 Email: support@cloutscape.org
- 💬 Discord: [Join the Den]
- 🌐 Website: https://cloutscape.org

---

## ⚖️ Legal

- **18+ Only** - Must be of legal gambling age
- **Jurisdiction Check** - Ensure gambling is legal in your area
- **Responsible Gaming** - Set limits, seek help if needed
- **Terms of Service** - Read [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)

---

## 🔥 Why Degens777Den?

We're **NOT** like other casinos:
- ❌ No manipulated RTP
- ❌ No hidden house edge adjustments
- ❌ No predatory bonus traps
- ❌ No fake "provably fair" schemes
- ❌ No withdrawal delays to trap funds

We're a **FAMILY** of degens who demand:
- ✅ Real transparency (97% RTP, always)
- ✅ Verifiable fairness (every seed public)
- ✅ Community over profit
- ✅ Quality over quantity (350 player cap)

**"All in. Ben Motto."** 🎲

Read the full manifesto: [WHY_DEGENS777DEN.md](WHY_DEGENS777DEN.md)

---

## 📝 License

**© 2025 Degens777Den. All rights reserved.**

This is proprietary software. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 🚀 Roadmap (Phase 2)

Coming soon:
- 🧩 **Mines** - Minesweeper-style game
- 🎰 **Degen Slots** - RuneScape-inspired with reels, multipliers, bonus rounds
- 🃏 **Omaha Poker** - Hourly tournaments with 10M GP prize pool
- 🔒 **Privacy Toggles** - Hide username from leaderboard/chat
- 💬 **Enhanced Forum** - Community posts, POPs, vouchers
- 🔗 **Discord OAuth** - Login with Discord

---

**Built with obsidian and gold. Designed for degens, by degens.** 🐺🔥

**Play at: [cloutscape.org](https://cloutscape.org)**
