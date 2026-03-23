# 🚀 QUICK START - Degens777Den Deployment

## Zero-Error, One-Command Deployment

---

## 📋 Prerequisites

**You need**:
- Ubuntu 20.04+ server
- Root access (`sudo`)
- 2GB+ RAM
- Domain pointed to server (cloutscape.org)

**That's it!** Everything else is automated.

---

## ⚡ DEPLOY IN 3 STEPS

### **Step 1: Clone Repository**
```bash
git clone https://github.com/damienmarx/Degens777Den.git
cd Degens777Den
```

### **Step 2: Run Deployment Script**
```bash
sudo bash deploy-degensden.sh
```

**This will automatically**:
- ✅ Install Node.js, Python, MongoDB, Nginx
- ✅ Setup MongoDB with authentication
- ✅ Install all dependencies
- ✅ Build frontend
- ✅ Configure services (Supervisor)
- ✅ Start backend, frontend, Discord bot
- ✅ Setup Nginx reverse proxy

**Duration**: 5-10 minutes

### **Step 3: Configure Secrets**
```bash
nano /opt/degensden/backend/.env
```

**Required changes**:
```env
# Generate strong secret (32+ characters)
JWT_SECRET="your-super-secret-key-here"

# Change default password
ADMIN_PASSWORD="YourStrongPassword123!"

# Add YOUR crypto wallets
WALLET_BTC="your-bitcoin-address"
WALLET_ETH="your-ethereum-address"
WALLET_LTC="your-litecoin-address"

# Discord bot (optional but recommended)
DISCORD_BOT_TOKEN="your-discord-bot-token"
```

**Restart services**:
```bash
sudo supervisorctl restart all
```

---

## 🤖 Discord Bot Setup (Optional)

### **1. Create Discord Bot**
1. Go to: https://discord.com/developers/applications
2. Click "New Application" → Name it "Degens777Den"
3. Go to "Bot" tab → Click "Add Bot"
4. Copy the **Token**
5. Enable "Message Content Intent" and "Server Members Intent"

### **2. Invite Bot to Server**
Use this URL (replace CLIENT_ID):
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot
```

**Permissions needed**: Administrator (for server setup)

### **3. Configure Bot**
```bash
nano /opt/degensden/backend/.env
```

Add:
```env
DISCORD_BOT_TOKEN="your_token_here"
DISCORD_GUILD_ID="your_server_id"
```

**Restart bot**:
```bash
sudo supervisorctl restart degensden-discord-bot
```

### **4. Setup Discord Server**
In your Discord server, type:
```
!setup
```

This creates:
- ✅ All categories (Information, Community, Casino, OSRS, Support)
- ✅ All channels (welcome, general-chat, big-wins, etc.)
- ✅ Roles (Alpha Wolf, Pack Leader, VIP Degen, Degen)

### **5. Test Onboarding**
- Join the server with a test account
- Bot will:
  - ✅ Send DM with wolf pack onboarding
  - ✅ Welcome in #welcome channel
  - ✅ Auto-assign "Degen" role

---

## ☁️ Cloudflare Tunnel Setup

### **1. Login**
```bash
cloudflared tunnel login
```

This opens browser - login to Cloudflare.

### **2. Create Tunnel**
```bash
cloudflared tunnel create kodakclout-prod
```

Note the **Tunnel ID** shown.

### **3. Route DNS**
```bash
cloudflared tunnel route dns kodakclout-prod cloutscape.org
```

### **4. Create Config**
```bash
nano ~/.cloudflared/config.yml
```

**Paste** (replace YOUR-TUNNEL-ID):
```yaml
tunnel: YOUR-TUNNEL-ID
credentials-file: /root/.cloudflared/YOUR-TUNNEL-ID.json

ingress:
  - hostname: cloutscape.org
    service: http://localhost:80
  - hostname: www.cloutscape.org
    service: http://localhost:80
  - service: http_status:404
```

### **5. Start Tunnel**
```bash
cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### **6. Verify**
Visit: https://cloutscape.org

---

## ✅ Post-Deployment Checklist

- [ ] Visit http://localhost - should show casino
- [ ] Login with admin@degensden.com / admin123
- [ ] Change admin password in settings
- [ ] Add crypto wallet addresses to .env
- [ ] Configure Discord bot token
- [ ] Run !setup in Discord
- [ ] Test Discord welcome DM (join with alt account)
- [ ] Setup Cloudflare tunnel
- [ ] Visit https://cloutscape.org
- [ ] Test games (play dice, keno, etc.)
- [ ] Verify VIP progress bar works
- [ ] Test KodakGP gold rates page

---

## 📊 Managing Services

### **View Status**
```bash
sudo supervisorctl status
```

### **Restart Services**
```bash
# Restart all
sudo supervisorctl restart all

# Restart individual
sudo supervisorctl restart degensden-backend
sudo supervisorctl restart degensden-frontend
sudo supervisorctl restart degensden-discord-bot
```

### **View Logs**
```bash
# Backend logs
tail -f /var/log/supervisor/degensden-backend.out.log

# Discord bot logs
tail -f /var/log/supervisor/degensden-discord.out.log

# Frontend logs
tail -f /var/log/supervisor/degensden-frontend.out.log
```

### **Check MongoDB**
```bash
mongosh "mongodb://admin:monalisa@localhost:27017/?authSource=admin"

use degensden_casino
show collections
db.users.countDocuments()
db.bets.find().limit(5)
```

---

## 🐛 Troubleshooting

### **Backend won't start**
```bash
# Check logs
tail -50 /var/log/supervisor/degensden-backend.err.log

# Common issues:
# - MongoDB not running: sudo systemctl start mongod
# - Missing dependencies: cd /opt/degensden/backend && source venv/bin/activate && pip install -r requirements.txt
# - Port in use: sudo lsof -i :8001
```

### **Frontend won't build**
```bash
# Rebuild
cd /opt/degensden/frontend
yarn install
yarn build

# Restart
sudo supervisorctl restart degensden-frontend
```

### **Discord bot not responding**
```bash
# Check logs
tail -50 /var/log/supervisor/degensden-discord.err.log

# Verify token
grep DISCORD_BOT_TOKEN /opt/degensden/backend/.env

# Restart bot
sudo supervisorctl restart degensden-discord-bot
```

### **Can't access site**
```bash
# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check Cloudflare tunnel
sudo systemctl status cloudflared

# Check services
sudo supervisorctl status
```

---

## 🎯 Common Tasks

### **Add New Admin**
```bash
mongosh "mongodb://admin:monalisa@localhost:27017/?authSource=admin"

use degensden_casino
db.users.updateOne(
  {email: "user@example.com"},
  {$set: {is_admin: true}}
)
```

### **Reset User Password**
```bash
# User must go through "Forgot Password" flow
# Or manually set in database (requires bcrypt hash)
```

### **View Live Bets**
```bash
mongosh "mongodb://admin:monalisa@localhost:27017/?authSource=admin"

use degensden_casino
db.bets.find().sort({created_at: -1}).limit(10)
```

### **Backup Database**
```bash
mongodump --uri="mongodb://admin:monalisa@localhost:27017/?authSource=admin" --out=/backup/degensden-$(date +%Y%m%d)
```

---

## 📞 Need Help?

**Documentation**:
- Full guide: `/app/DEPLOYMENT_GUIDE.md`
- Environment vars: `/app/ENV_VARIABLES_GUIDE.md`
- Terms of Service: `/app/TERMS_OF_SERVICE.md`

**Support**:
- Email: support@cloutscape.org
- Discord: Run !help in server
- GitHub: https://github.com/damienmarx/Degens777Den/issues

---

## 🔥 You're Ready!

**Your casino is live at:**
- Local: http://localhost
- Production: https://cloutscape.org

**Discord bot is running:**
- Wolf pack onboarding active
- Welcome DMs sending
- Channel announcements working

**All systems operational.** 🐺

**"All In. Ben Motto."** 🎲

---

**© 2025 Degens777Den - Built for degens, by degens.**
