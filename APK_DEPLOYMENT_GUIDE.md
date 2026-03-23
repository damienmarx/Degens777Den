# Degens777Den - APK Deployment & Cloudflare Tunnel Guide

This guide walks you through deploying your Degens777Den casino as an Android APK with full Cloudflare tunnel integration. The APK will work seamlessly with Discord webhooks and the web app.

---

## 📋 Prerequisites

- **Cloudflare Account** (free tier works)
- **GitHub Account** (for automated APK builds)
- **Android Device** (for testing)
- **Local Backend Running** (see below)

---

## 🚀 Step 1: Start Your Backend Locally

Before setting up the tunnel, ensure your backend is running:

```bash
cd /home/ubuntu/Degens777Den/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Make sure MongoDB is running
sudo systemctl start mongod

# Start the backend API
python server.py
```

The backend should be running on `http://localhost:8001`.

---

## 🌐 Step 2: Set Up Cloudflare Tunnel

### Option A: Automated Setup (Recommended)

```bash
cd /home/ubuntu/Degens777Den
bash cloudflare-tunnel-setup.sh
```

This script will:
1. Install `cloudflared` if needed
2. Authenticate with your Cloudflare account
3. Create a tunnel named `kodakclout-prod`
4. Configure routing for frontend, backend, and WebSocket

### Option B: Manual Setup

1. **Install cloudflared:**
   ```bash
   curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared.deb
   ```

2. **Authenticate:**
   ```bash
   cloudflared tunnel login
   ```

3. **Create tunnel:**
   ```bash
   cloudflared tunnel create kodakclout-prod
   ```

4. **Create config file** at `~/.cloudflared/config.yml`:
   ```yaml
   tunnel: kodakclout-prod
   credentials-file: /home/ubuntu/.cloudflared/kodakclout-prod.json

   ingress:
     - hostname: kodakclout-prod.workers.dev
       service: http://localhost:3000
     - hostname: api.kodakclout-prod.workers.dev
       service: http://localhost:8001
     - hostname: ws.kodakclout-prod.workers.dev
       service: http://localhost:8001
     - service: http_status:404
   ```

5. **Start the tunnel:**
   ```bash
   cloudflared tunnel run kodakclout-prod
   ```

---

## 📱 Step 3: Build the APK

### Option A: Automated Build (GitHub Actions)

1. **Push your code to GitHub:**
   ```bash
   cd /home/ubuntu/Degens777Den
   git add .
   git commit -m "Add APK and tunnel configuration"
   git push origin main
   ```

2. **Set up GitHub Secrets:**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `ANDROID_SIGNING_KEY`: Base64 encoded keystore file
     - `ANDROID_KEY_ALIAS`: Your key alias
     - `ANDROID_KEYSTORE_PASSWORD`: Keystore password
     - `ANDROID_KEY_PASSWORD`: Key password
     - `DISCORD_WEBHOOK_URL`: Your Discord webhook (optional)

3. **Trigger the build:**
   - Go to Actions tab → Build Android APK → Run workflow
   - Or push a tag: `git tag v1.0.0 && git push origin v1.0.0`

4. **Download APK:**
   - Go to the workflow run → Artifacts → `degens777den-apk`

### Option B: Manual Build (Local)

```bash
cd /home/ubuntu/Degens777Den/frontend

# Install dependencies
npm install --legacy-peer-deps

# Build production frontend
npm run build

# Install Capacitor CLI
npm install -g @capacitor/cli

# Add Android platform
npx cap add android

# Copy web assets
npx cap copy

# Build APK (requires Android SDK)
cd android
./gradlew assembleRelease

# Signed APK will be at: app/build/outputs/apk/release/app-release.apk
```

---

## 🔧 Step 4: Configure APK for Tunnel

The APK is automatically configured to use the Cloudflare tunnel via the `.env.production` file:

```env
REACT_APP_BACKEND_URL=https://kodakclout-prod.workers.dev
REACT_APP_WS_URL=wss://kodakclout-prod.workers.dev/ws
```

**No additional configuration needed!** The APK will:
- ✅ Connect to your backend via the tunnel
- ✅ Send Discord webhook notifications
- ✅ Support real-time chat via WebSocket
- ✅ Work offline with service worker caching

---

## 📲 Step 5: Install & Test APK

### Install on Android Device

1. **Enable Developer Mode:**
   - Settings → About Phone → Tap "Build Number" 7 times
   - Go back to Settings → Developer Options → Enable USB Debugging

2. **Connect device via USB:**
   ```bash
   adb devices
   ```

3. **Install APK:**
   ```bash
   adb install -r /path/to/app-release.apk
   ```

4. **Or download directly:**
   - Transfer the APK file to your device
   - Open file manager → Tap APK → Install

### Test the APK

1. **Launch the app** from your home screen
2. **Register/Login** with your account
3. **Test a bet** to verify backend connection
4. **Send a chat message** to test WebSocket
5. **Check Discord** for webhook notifications

---

## 🔌 Step 6: Keep Tunnel Running

### Option A: Background Process

```bash
nohup cloudflared tunnel run kodakclout-prod > /tmp/cloudflared.log 2>&1 &
```

### Option B: Systemd Service

Create `/etc/systemd/system/cloudflared.service`:

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/bin/cloudflared tunnel run kodakclout-prod
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### Option C: Docker Container

```bash
docker run -d \
  --name cloudflared \
  --restart unless-stopped \
  -v ~/.cloudflared:/root/.cloudflared \
  cloudflare/cloudflared:latest \
  tunnel run kodakclout-prod
```

---

## 🎯 Verification Checklist

- [ ] Backend running on `http://localhost:8001`
- [ ] MongoDB running and accessible
- [ ] Cloudflare tunnel active and running
- [ ] APK installed on Android device
- [ ] Can login to APK
- [ ] Can place a bet in APK
- [ ] Chat messages appear in real-time
- [ ] Discord receives webhook notifications
- [ ] Web app accessible at `https://kodakclout-prod.workers.dev`
- [ ] APK and web app show same balance/history

---

## 🐛 Troubleshooting

### APK can't connect to backend
- **Check tunnel status:** `cloudflared tunnel info kodakclout-prod`
- **Verify backend running:** `curl http://localhost:8001/api/health`
- **Check firewall:** Ensure port 8001 is not blocked

### Discord webhooks not working
- **Verify webhook URL** in `.env` file
- **Check webhook exists** in Discord server
- **Monitor logs:** `tail -f /tmp/cloudflared.log`

### WebSocket connection fails
- **Ensure tunnel config includes WebSocket route**
- **Check browser console** for connection errors
- **Verify `wss://` protocol** is being used

### APK crashes on startup
- **Check Android logs:** `adb logcat | grep -i degens`
- **Verify API endpoint** in `.env.production`
- **Test with web app first** to isolate issues

---

## 📊 Monitoring

### View Tunnel Logs
```bash
cloudflared tunnel logs kodakclout-prod
```

### Monitor Backend
```bash
tail -f /var/log/degensden/backend.log
```

### Check APK Connectivity
```bash
adb logcat | grep -i "api\|network\|http"
```

---

## 🔐 Security Notes

1. **Always use HTTPS** (tunnel provides this automatically)
2. **Rotate JWT secrets** in production
3. **Enable rate limiting** in backend
4. **Monitor Discord webhook** for abuse
5. **Keep APK signed** with your keystore
6. **Update dependencies** regularly

---

## 📈 Next Steps

1. **Set up monitoring** (Sentry, DataDog, etc.)
2. **Configure auto-scaling** if needed
3. **Set up CI/CD pipeline** for automatic releases
4. **Create app store listings** (Google Play, etc.)
5. **Implement analytics** to track user behavior

---

## 📞 Support

For issues or questions:
- Check logs: `cloudflared tunnel logs kodakclout-prod`
- Review backend logs: `/var/log/degensden/backend.log`
- Test with web app first to isolate APK issues
- Verify all environment variables are set correctly

---

**Status:** ✅ Ready for Production  
**Last Updated:** March 23, 2026  
**Version:** 1.0.0
