# Degens777Den - External Dependencies & Integrations Report

This report outlines all external services, APIs, and dependencies identified within the Degens777Den project. Understanding these is crucial for a successful production deployment.

---

## 🚀 1. Core Infrastructure Dependencies

| Dependency | Purpose | Requirement |
|------------|---------|-------------|
| **MongoDB** | Primary Database | Required (Self-hosted or Atlas) |
| **Node.js / NPM** | Frontend Build & Runtime | Required (v20.x recommended) |
| **Python 3.11+** | Backend API Runtime | Required |
| **Nginx** | Web Server / Reverse Proxy | Recommended for Production |
| **Docker** | Containerization | Optional (but recommended) |

---

## 🔗 2. External Service Integrations

### 💬 Discord Integration
The project heavily relies on Discord for notifications and community engagement.
- **Discord Webhooks**: Used for real-time notifications of deposits, withdrawals, and game wins.
- **Discord Bot**: A custom bot is included (`discord_bot_v2.py`) for community management.
- **Discord OAuth**: Configuration exists but is currently disabled by default (`ENABLE_DISCORD_OAUTH=false`).
- **Action Required**: You must provide a `DISCORD_WEBHOOK_URL` and `DISCORD_BOT_TOKEN` in the `.env` file.

### 💰 OSRS / KodakGP Integration
The project features a specialized integration for Old School RuneScape (OSRS) gold trading.
- **KodakGP**: A trusted OSRS gold provider integration is built-in.
- **Manual Verification**: Currently, GP deposits and services are handled through manual verification workflows triggered by Discord notifications.
- **Rates**: GP buy/sell rates are currently hardcoded in `server.py` but can be overridden via environment variables.

### 💳 Crypto Payment Processing
- **Status**: The current implementation uses **placeholder addresses** and **manual verification**.
- **Self-Hosted**: There is no external payment gateway (like Stripe or Coinbase Commerce) integrated by default.
- **Action Required**: You must update the `ADMIN_WALLETS` in your `.env` file with your real wallet addresses.
- **Verification**: In the current state, an admin must manually verify blockchain transactions and credit user accounts via the admin panel or database.

---

## 🌐 3. Frontend External Resources

The frontend is designed to be lean, but it does fetch a few resources from external CDNs:
- **Google Fonts**: Fetches `Orbitron`, `Space Mono`, and `Outfit` from `fonts.googleapis.com`.
- **Shadcn UI**: Uses schemas from `ui.shadcn.com` during development/component setup.
- **Pexels/Unsplash**: Some placeholder images in `design_guidelines.json` point to external URLs.

---

## 🔒 4. Security & Environment Configuration

All sensitive configurations are managed via environment variables. Ensure the following are set before going live:

| Variable | Importance | Description |
|----------|------------|-------------|
| `JWT_SECRET` | **CRITICAL** | Change this to a long, random string. |
| `MONGO_URL` | **CRITICAL** | Ensure your MongoDB instance is secured with a password. |
| `ADMIN_PASSWORD` | **CRITICAL** | Change the default `Wolf777Pack2025!` password. |
| `CORS_ORIGINS` | **HIGH** | Restrict this to your production domain (e.g., `https://cloutscape.org`). |
| `DISCORD_WEBHOOK_URL` | **HIGH** | Required for receiving transaction notifications. |

---

## 🛠️ 5. Third-Party Libraries (Key Packages)

### Backend (Python)
- `fastapi`: Web framework
- `motor`: Async MongoDB driver
- `pyjwt`: Authentication
- `bcrypt`: Password hashing
- `aiohttp`: Async HTTP client (for webhooks)

### Frontend (React)
- `lucide-react`: Icons
- `recharts`: Data visualization
- `tailwindcss`: Styling
- `framer-motion`: Animations

---

## 📝 6. Summary of "External" Risks

1. **Manual Payments**: Since there's no automated crypto payment gateway, the speed of deposits/withdrawals depends on admin availability.
2. **Discord Dependency**: If Discord is down or your webhook is deleted, you will lose real-time visibility into platform activity.
3. **Hardcoded Rates**: Ensure you regularly update the OSRS GP rates in `server.py` or implement a dynamic fetcher if needed.

---

**Report Generated:** March 23, 2026  
**Status:** ✅ All dependencies identified and documented.
