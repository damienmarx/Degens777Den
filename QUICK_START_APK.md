# 🚀 Degens777Den APK - Quick Start Guide

Get your casino APK running with Cloudflare tunnel in 5 minutes!

---

## ⚡ TL;DR - 5 Minute Setup

```bash
# 1. Start backend
cd /home/ubuntu/Degens777Den/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python server.py

# 2. Setup tunnel (in new terminal)
cd /home/ubuntu/Degens777Den
bash cloudflare-tunnel-setup.sh
cloudflared tunnel run kodakclout-prod

# 3. Build APK (in new terminal)
cd /home/ubuntu/Degens777Den/frontend
npm install --legacy-peer-deps
npm run build
npm install -g @capacitor/cli
npx cap add android
npx cap copy
cd android && ./gradlew assembleRelease

# 4. Install on phone
adb install -r app/build/outputs/apk/release/app-release.apk

# 5. Open APK and start playing!
```

---

## 📱 What Works in the APK

✅ **All 6 Casino Games** (Dice, Crash, Keno, Wheel, Plinko, Limbo)  
✅ **Multi-Currency Wallet** (BTC, ETH, LTC, USDC, USDT, OSRS GP)  
✅ **Real-Time Chat** (WebSocket via tunnel)  
✅ **Discord Notifications** (Deposits, Wins, Withdrawals)  
✅ **VIP System & Rakeback** (Automatic rewards)  
✅ **Provably Fair** (Verify every bet)  
✅ **Referral Program** (Share and earn)  
✅ **Offline Support** (PWA caching)  

---

## 🔗 Tunnel Integration

Your APK automatically connects to:

| Component | Tunnel URL |
|-----------|-----------|
| **Frontend** | `https://kodakclout-prod.workers.dev` |
| **API** | `https://api.kodakclout-prod.workers.dev` |
| **WebSocket** | `wss://ws.kodakclout-prod.workers.dev` |

**No configuration needed!** The APK reads from `.env.production` automatically.

---

## 🤖 Discord Integration

Your APK sends notifications for:
- 🎰 Big wins (5x+ multiplier)
- 💰 Deposits received
- 💸 Withdrawals requested
- 🎉 Referral signups

Just set `DISCORD_WEBHOOK_URL` in your `.env` file.

---

## 📋 Prerequisites

- ✅ Java 11+ installed
- ✅ Android SDK installed
- ✅ Node.js 20+ installed
- ✅ Python 3.11+ installed
- ✅ MongoDB running
- ✅ Cloudflare account (free)

---

## 🔧 Troubleshooting

### APK won't connect to backend
```bash
# Check tunnel is running
cloudflared tunnel info kodakclout-prod

# Check backend is responding
curl https://api.kodakclout-prod.workers.dev/api/health

# Check logs
tail -f /tmp/cloudflared.log
```

### Chat not working
```bash
# Verify WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  wss://ws.kodakclout-prod.workers.dev/ws
```

### Discord webhooks not firing
```bash
# Check webhook URL in .env
grep DISCORD_WEBHOOK_URL /home/ubuntu/Degens777Den/backend/.env

# Test webhook manually
curl -X POST $DISCORD_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message"}'
```

---

## 📊 Monitoring

```bash
# Backend logs
sudo journalctl -u degens-backend.service -f

# Tunnel logs
tail -f /tmp/cloudflared.log

# MongoDB logs
sudo journalctl -u mongod -f

# APK logs (on device)
adb logcat | grep -i degens
```

---

## 🎯 Next Steps

1. **Test on multiple devices** (phone, tablet)
2. **Set up auto-scaling** if expecting high traffic
3. **Configure analytics** (Sentry, DataDog)
4. **Submit to Google Play Store** for distribution
5. **Set up CI/CD** for automatic APK releases

---

## 📞 Support

- 📖 Full guide: `APK_DEPLOYMENT_GUIDE.md`
- 🔐 Security: `EXTERNAL_DEPENDENCIES_REPORT.md`
- 🚀 Production: `PRODUCTION_DEPLOYMENT.md`

---

**Status:** ✅ Ready to Deploy  
**Version:** 1.0.0  
**Last Updated:** March 23, 2026
