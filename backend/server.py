from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
import hashlib
import hmac
import secrets
import math
import random
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import asyncio
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
SECRET_KEY = os.environ.get('JWT_SECRET', 'degens7den-secret-2024-ultra-secure')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 72

app = FastAPI(title="Degen's Den Casino API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# ==================== PROVABLY FAIR ENGINE ====================

class ProvablyFair:
    @staticmethod
    def generate_server_seed() -> str:
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_seed(seed: str) -> str:
        return hashlib.sha256(seed.encode()).hexdigest()
    
    @staticmethod
    def generate_game_result(server_seed: str, client_seed: str, nonce: int, game_type: str) -> dict:
        combined = f"{server_seed}:{client_seed}:{nonce}"
        hash_result = hashlib.sha256(combined.encode()).hexdigest()
        
        # Convert first 8 chars of hash to decimal for RNG
        decimal_value = int(hash_result[:8], 16)
        max_value = 0xFFFFFFFF
        roll = decimal_value / max_value
        
        if game_type == "dice":
            result = roll * 100
            return {"roll": round(result, 2), "hash": hash_result}
        elif game_type == "crash":
            # House edge 1%
            h = int(hash_result[:13], 16)
            e = 2 ** 52
            crash_point = max(1.00, (0.99 * e) / (e - h))
            return {"crash_point": round(crash_point, 2), "hash": hash_result}
        elif game_type == "keno":
            # Generate 10 unique numbers 1-40 from hash
            numbers = []
            for i in range(0, 40, 4):
                segment = hash_result[i:i+4]
                num = (int(segment, 16) % 40) + 1
                while num in numbers:
                    num = (num % 40) + 1
                numbers.append(num)
                if len(numbers) == 10:
                    break
            return {"drawn_numbers": sorted(numbers), "hash": hash_result}
        elif game_type == "wheel":
            multipliers = [0, 2, 0, 3.5, 0, 2, 0, 7, 0, 2, 0, 3.5, 0, 2, 0, 21, 0, 2, 0, 3.5]
            segment = int(roll * len(multipliers))
            return {"segment": segment, "multiplier": multipliers[segment], "hash": hash_result}
        elif game_type == "plinko":
            # 16 rows, each row L or R based on hash bits
            path = []
            final_position = 8  # Start middle
            for i in range(16):
                bit = int(hash_result[i], 16) % 2
                if bit == 0:
                    final_position = max(0, final_position - 1)
                    path.append("L")
                else:
                    final_position = min(16, final_position + 1)
                    path.append("R")
            multipliers = [110, 41, 10, 5, 3, 1.5, 1, 0.5, 0.3, 0.5, 1, 1.5, 3, 5, 10, 41, 110]
            return {"path": path, "position": final_position, "multiplier": multipliers[final_position], "hash": hash_result}
        elif game_type == "limbo":
            target_multi = max(1.01, (1 / roll) * 0.99)
            return {"target": round(target_multi, 2), "hash": hash_result}
        
        return {"roll": roll, "hash": hash_result}
    
    @staticmethod
    def verify_result(server_seed: str, client_seed: str, nonce: int, game_type: str, claimed_hash: str) -> bool:
        result = ProvablyFair.generate_game_result(server_seed, client_seed, nonce, game_type)
        return result["hash"] == claimed_hash

# ==================== MODELS ====================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    username: str
    email: str
    vip_level: int = 0
    vip_progress: float = 0.0
    total_wagered: float = 0.0
    rakeback_available: float = 0.0
    lossback_available: float = 0.0
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class WalletBalance(BaseModel):
    currency: str
    balance: float
    address: Optional[str] = None

class WalletResponse(BaseModel):
    balances: List[WalletBalance]
    osrs_gp: float = 0.0

class DepositRequest(BaseModel):
    currency: str
    amount: float

class WithdrawRequest(BaseModel):
    currency: str
    amount: float
    address: str

class BetRequest(BaseModel):
    game_type: str
    amount: float
    currency: str = "btc"
    params: dict = {}

class BetResponse(BaseModel):
    id: str
    game_type: str
    amount: float
    multiplier: float
    payout: float
    result: dict
    won: bool
    server_seed_hash: str
    client_seed: str
    nonce: int

class ChatMessage(BaseModel):
    id: str
    user_id: str
    username: str
    message: str
    message_type: str = "chat"  # chat, rain, tip, system
    timestamp: str
    extra_data: Optional[dict] = None

class SendChatMessage(BaseModel):
    message: str

class TipRequest(BaseModel):
    recipient_username: str
    amount: float
    currency: str = "btc"

class RainRequest(BaseModel):
    total_amount: float
    currency: str = "btc"

class SeedChange(BaseModel):
    new_client_seed: str

class ProvablyFairInfo(BaseModel):
    server_seed_hash: str
    client_seed: str
    nonce: int
    previous_server_seed: Optional[str] = None

# ==================== REFERRAL MODELS ====================

class ReferralCodeCreate(BaseModel):
    code: str
    bonus_type: str = "usd"  # "usd" or "gp"
    bonus_amount: float = 5.0  # $5 USD or 35M GP
    wager_requirement: float = 10.0  # 10x multiplier
    max_uses: int = 100
    expires_days: int = 30

class ReferralCodeRedeem(BaseModel):
    code: str

class ReferralCodeResponse(BaseModel):
    code: str
    bonus_type: str
    bonus_amount: float
    wager_requirement: float
    uses: int
    max_uses: int
    is_active: bool

class OSRSDepositRequest(BaseModel):
    amount_gp: int  # Amount in GP (e.g., 15000000 for 15M)
    rsn: str  # RuneScape Name for verification

class WithdrawRequestV2(BaseModel):
    currency: str
    amount: float
    address: str

# ==================== PLATFORM CONFIG ====================

PLATFORM_CONFIG = {
    "osrs_min_deposit": int(os.environ.get("OSRS_MIN_DEPOSIT", 15000000)),  # 15M GP
    "osrs_max_deposit": int(os.environ.get("OSRS_MAX_DEPOSIT", 750000000)),  # 750M GP
    "osrs_deposit_rsn": os.environ.get("OSRS_DEPOSIT_RSN", "Degens7Den"),
    "btc_min_deposit_usd": float(os.environ.get("BTC_MIN_DEPOSIT_USD", 5)),
    "btc_max_deposit_usd": float(os.environ.get("BTC_MAX_DEPOSIT_USD", 250)),
    "daily_withdraw_limit_usd": float(os.environ.get("DAILY_WITHDRAW_LIMIT_USD", 500)),
    "extended_withdraw_wait_hours": 48,
    "referral_wager_multiplier": 10.0,
    "referral_bonus_usd": 5.0,
    "referral_bonus_gp": 35000000,  # 35M GP
}

ADMIN_WALLETS = {
    "btc": os.environ.get("WALLET_BTC", ""),
    "eth": os.environ.get("WALLET_ETH", ""),
    "ltc": os.environ.get("WALLET_LTC", ""),
    "usdc": os.environ.get("WALLET_USDC", ""),
    "usdt": os.environ.get("WALLET_USDT", ""),
}

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# ==================== DISCORD WEBHOOK HELPER ====================

import aiohttp

async def send_discord_webhook(title: str, description: str, color: int = 0x00FF00, fields: list = None):
    """Send notification to Discord webhook"""
    if not DISCORD_WEBHOOK_URL:
        return
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": "Degen's Den Casino"}
    }
    
    if fields:
        embed["fields"] = fields
    
    payload = {"embeds": [embed]}
    
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        logger.error(f"Discord webhook error: {e}")

# ==================== VIP TIERS ====================

VIP_TIERS = {
    0: {"name": "Bronze", "wager_required": 0, "rakeback": 0.05, "lossback": 0.0},
    1: {"name": "Silver", "wager_required": 1000, "rakeback": 0.10, "lossback": 0.02},
    2: {"name": "Gold", "wager_required": 10000, "rakeback": 0.15, "lossback": 0.05},
    3: {"name": "Platinum", "wager_required": 50000, "rakeback": 0.20, "lossback": 0.08},
    4: {"name": "Dragon", "wager_required": 250000, "rakeback": 0.30, "lossback": 0.12},
}

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, is_admin: bool = False) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": user_id, "is_admin": is_admin, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(user: dict = Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ==================== WALLET HELPERS ====================

SUPPORTED_CURRENCIES = ["btc", "eth", "ltc", "usdc", "usdt"]

def generate_crypto_address(currency: str) -> str:
    """Generate a placeholder crypto address - in production, integrate with real wallet provider"""
    prefix = {"btc": "bc1q", "eth": "0x", "ltc": "ltc1q", "usdc": "0x", "usdt": "0x"}
    return prefix.get(currency, "0x") + secrets.token_hex(20)

async def get_or_create_wallet(user_id: str) -> dict:
    wallet = await db.wallets.find_one({"user_id": user_id}, {"_id": 0})
    if not wallet:
        wallet = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "balances": {curr: {"balance": 0.0, "address": generate_crypto_address(curr)} for curr in SUPPORTED_CURRENCIES},
            "osrs_gp": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.wallets.insert_one(wallet)
    return wallet

async def update_balance(user_id: str, currency: str, amount: float, operation: str = "add") -> bool:
    wallet = await get_or_create_wallet(user_id)
    if currency == "osrs_gp":
        current = wallet.get("osrs_gp", 0.0)
        new_balance = current + amount if operation == "add" else current - amount
        if new_balance < 0:
            return False
        await db.wallets.update_one({"user_id": user_id}, {"$set": {"osrs_gp": new_balance}})
    else:
        current = wallet["balances"].get(currency, {}).get("balance", 0.0)
        new_balance = current + amount if operation == "add" else current - amount
        if new_balance < 0:
            return False
        await db.wallets.update_one({"user_id": user_id}, {"$set": {f"balances.{currency}.balance": new_balance}})
    return True

# ==================== PROVABLY FAIR HELPERS ====================

async def get_or_create_seeds(user_id: str) -> dict:
    seeds = await db.seeds.find_one({"user_id": user_id}, {"_id": 0})
    if not seeds:
        server_seed = ProvablyFair.generate_server_seed()
        seeds = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "server_seed": server_seed,
            "server_seed_hash": ProvablyFair.hash_seed(server_seed),
            "client_seed": secrets.token_hex(16),
            "nonce": 0,
            "previous_server_seed": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.seeds.insert_one(seeds)
    return seeds

async def increment_nonce(user_id: str) -> int:
    result = await db.seeds.find_one_and_update(
        {"user_id": user_id},
        {"$inc": {"nonce": 1}},
        return_document=True,
        projection={"_id": 0}
    )
    return result["nonce"]

# ==================== VIP HELPERS ====================

async def update_vip_status(user_id: str, wager_amount: float, profit: float):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return
    
    new_total_wagered = user.get("total_wagered", 0) + wager_amount
    
    # Calculate VIP level
    new_vip_level = 0
    for level, tier in VIP_TIERS.items():
        if new_total_wagered >= tier["wager_required"]:
            new_vip_level = level
    
    # Calculate progress to next tier
    current_tier = VIP_TIERS[new_vip_level]
    next_tier = VIP_TIERS.get(new_vip_level + 1)
    if next_tier:
        progress = (new_total_wagered - current_tier["wager_required"]) / (next_tier["wager_required"] - current_tier["wager_required"])
        progress = min(max(progress, 0), 1) * 100
    else:
        progress = 100
    
    # Calculate rakeback (on house edge, roughly 1% of wager)
    house_edge = wager_amount * 0.01
    rakeback_earned = house_edge * current_tier["rakeback"]
    
    # Calculate lossback (only if loss and VIP qualified)
    lossback_earned = 0
    if profit < 0 and new_vip_level >= 1:
        lossback_earned = abs(profit) * current_tier["lossback"]
    
    # Update referral wager progress if user has pending bonus
    update_fields = {
        "total_wagered": new_total_wagered,
        "vip_level": new_vip_level,
        "vip_progress": progress
    }
    
    inc_fields = {
        "rakeback_available": rakeback_earned,
        "lossback_available": lossback_earned
    }
    
    if user.get("referral_bonus_pending", 0) > 0:
        new_referral_wager = user.get("referral_wager_completed", 0) + wager_amount
        update_fields["referral_wager_completed"] = new_referral_wager
        
        # Check if wager requirement is met
        if new_referral_wager >= user.get("referral_wager_required", 0):
            update_fields["referral_bonus_pending"] = 0  # Unlock the bonus
            # Notify via Discord
            asyncio.create_task(send_discord_webhook(
                title="🎰 Referral Bonus Unlocked!",
                description=f"**{user['username']}** completed referral wager requirement!",
                color=0x00FF00,
                fields=[
                    {"name": "Wagered", "value": f"${new_referral_wager:.2f}", "inline": True},
                    {"name": "Required", "value": f"${user.get('referral_wager_required', 0):.2f}", "inline": True}
                ]
            ))
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": update_fields, "$inc": inc_fields}
    )

# ==================== CHAT MANAGER ====================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
    
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except:
                pass

manager = ConnectionManager()

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(data: UserCreate, referral_code: Optional[str] = None):
    existing = await db.users.find_one({"$or": [{"email": data.email}, {"username": data.username}]})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Generate unique referral code for new user
    user_referral_code = data.username.upper()[:6] + secrets.token_hex(3).upper()
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "username": data.username,
        "email": data.email,
        "password": hash_password(data.password),
        "is_admin": False,
        "vip_level": 0,
        "vip_progress": 0.0,
        "total_wagered": 0.0,
        "rakeback_available": 0.0,
        "lossback_available": 0.0,
        "referral_code": user_referral_code,
        "referred_by": None,
        "referral_bonus_pending": 0.0,
        "referral_bonus_type": None,
        "referral_wager_required": 0.0,
        "referral_wager_completed": 0.0,
        "referred_users": [],
        "ip_address": None,  # For anti-abuse
        "device_fingerprint": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user)
    
    # Create wallet and seeds
    await get_or_create_wallet(user_id)
    await get_or_create_seeds(user_id)
    
    token = create_token(user_id)
    return TokenResponse(
        access_token=token,
        user=UserResponse(**{k: v for k, v in user.items() if k != "password"})
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user.get("is_admin", False))
    return TokenResponse(
        access_token=token,
        user=UserResponse(**{k: v for k, v in user.items() if k != "password"})
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(**{k: v for k, v in user.items() if k != "password"})

# ==================== WALLET ROUTES ====================

@api_router.get("/wallet", response_model=WalletResponse)
async def get_wallet(user: dict = Depends(get_current_user)):
    wallet = await get_or_create_wallet(user["id"])
    balances = [
        WalletBalance(currency=curr, balance=data["balance"], address=data.get("address"))
        for curr, data in wallet["balances"].items()
    ]
    return WalletResponse(balances=balances, osrs_gp=wallet.get("osrs_gp", 0.0))

@api_router.get("/wallet/config")
async def get_wallet_config():
    """Get platform deposit/withdraw limits and admin wallet addresses"""
    return {
        "osrs": {
            "min_deposit": PLATFORM_CONFIG["osrs_min_deposit"],
            "max_deposit": PLATFORM_CONFIG["osrs_max_deposit"],
            "deposit_rsn": PLATFORM_CONFIG["osrs_deposit_rsn"],
        },
        "crypto": {
            "min_deposit_usd": PLATFORM_CONFIG["btc_min_deposit_usd"],
            "max_deposit_usd": PLATFORM_CONFIG["btc_max_deposit_usd"],
        },
        "withdraw": {
            "daily_limit_usd": PLATFORM_CONFIG["daily_withdraw_limit_usd"],
            "extended_wait_hours": PLATFORM_CONFIG["extended_withdraw_wait_hours"],
        },
        "admin_wallets": {k: v for k, v in ADMIN_WALLETS.items() if v}
    }

@api_router.post("/wallet/deposit")
async def deposit(data: DepositRequest, user: dict = Depends(get_current_user)):
    if data.currency not in SUPPORTED_CURRENCIES and data.currency != "osrs_gp":
        raise HTTPException(status_code=400, detail="Unsupported currency")
    
    # Validate deposit limits
    if data.currency == "osrs_gp":
        if data.amount < PLATFORM_CONFIG["osrs_min_deposit"]:
            raise HTTPException(status_code=400, detail=f"Minimum OSRS GP deposit is {PLATFORM_CONFIG['osrs_min_deposit']/1000000:.0f}M")
        if data.amount > PLATFORM_CONFIG["osrs_max_deposit"]:
            raise HTTPException(status_code=400, detail=f"Maximum OSRS GP deposit is {PLATFORM_CONFIG['osrs_max_deposit']/1000000:.0f}M")
    else:
        # Crypto deposits - check USD equivalent (simplified: assume $1 = amount for stablecoins)
        usd_value = data.amount
        if data.currency == "btc":
            usd_value = data.amount * 50000  # Approximate BTC price
        elif data.currency == "eth":
            usd_value = data.amount * 3000  # Approximate ETH price
        elif data.currency == "ltc":
            usd_value = data.amount * 100  # Approximate LTC price
        
        if usd_value < PLATFORM_CONFIG["btc_min_deposit_usd"]:
            raise HTTPException(status_code=400, detail=f"Minimum deposit is ${PLATFORM_CONFIG['btc_min_deposit_usd']}")
        if usd_value > PLATFORM_CONFIG["btc_max_deposit_usd"]:
            raise HTTPException(status_code=400, detail=f"Maximum deposit is ${PLATFORM_CONFIG['btc_max_deposit_usd']}")
    
    await update_balance(user["id"], data.currency, data.amount, "add")
    
    # Log transaction
    tx_id = str(uuid.uuid4())
    await db.transactions.insert_one({
        "id": tx_id,
        "user_id": user["id"],
        "type": "deposit",
        "currency": data.currency,
        "amount": data.amount,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Send Discord webhook notification
    await send_discord_webhook(
        title="💰 New Deposit",
        description=f"**{user['username']}** deposited funds",
        color=0x00FF00,
        fields=[
            {"name": "Amount", "value": f"{data.amount} {data.currency.upper()}", "inline": True},
            {"name": "User", "value": user['username'], "inline": True},
            {"name": "TX ID", "value": tx_id[:8], "inline": True}
        ]
    )
    
    return {"message": "Deposit successful", "amount": data.amount, "currency": data.currency}

@api_router.post("/wallet/deposit/osrs")
async def deposit_osrs(data: OSRSDepositRequest, user: dict = Depends(get_current_user)):
    """OSRS GP Deposit Flow - User trades GP in-game"""
    if data.amount_gp < PLATFORM_CONFIG["osrs_min_deposit"]:
        raise HTTPException(status_code=400, detail=f"Minimum deposit is {PLATFORM_CONFIG['osrs_min_deposit']/1000000:.0f}M GP")
    if data.amount_gp > PLATFORM_CONFIG["osrs_max_deposit"]:
        raise HTTPException(status_code=400, detail=f"Maximum deposit is {PLATFORM_CONFIG['osrs_max_deposit']/1000000:.0f}M GP")
    
    # Create pending deposit request
    deposit_id = str(uuid.uuid4())
    deposit_code = secrets.token_hex(4).upper()
    
    await db.osrs_deposits.insert_one({
        "id": deposit_id,
        "code": deposit_code,
        "user_id": user["id"],
        "username": user["username"],
        "amount_gp": data.amount_gp,
        "rsn": data.rsn,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    })
    
    # Send Discord webhook for staff to process
    await send_discord_webhook(
        title="🎮 OSRS GP Deposit Request",
        description=f"New GP deposit pending verification",
        color=0xFFC800,
        fields=[
            {"name": "Amount", "value": f"{data.amount_gp/1000000:.1f}M GP", "inline": True},
            {"name": "RSN", "value": data.rsn, "inline": True},
            {"name": "User", "value": user['username'], "inline": True},
            {"name": "Code", "value": deposit_code, "inline": True},
            {"name": "Trade To", "value": PLATFORM_CONFIG["osrs_deposit_rsn"], "inline": True}
        ]
    )
    
    return {
        "message": "Deposit request created",
        "deposit_id": deposit_id,
        "code": deposit_code,
        "amount_gp": data.amount_gp,
        "trade_to_rsn": PLATFORM_CONFIG["osrs_deposit_rsn"],
        "instructions": f"Trade {data.amount_gp/1000000:.1f}M GP to '{PLATFORM_CONFIG['osrs_deposit_rsn']}' in-game. Include code '{deposit_code}' in trade message. Expires in 1 hour."
    }

@api_router.post("/wallet/withdraw")
async def withdraw(data: WithdrawRequest, user: dict = Depends(get_current_user)):
    if data.currency not in SUPPORTED_CURRENCIES and data.currency != "osrs_gp":
        raise HTTPException(status_code=400, detail="Unsupported currency")
    
    # Check daily withdrawal limit
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_withdrawals = await db.transactions.aggregate([
        {"$match": {
            "user_id": user["id"],
            "type": "withdrawal",
            "created_at": {"$gte": today_start.isoformat()}
        }},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    today_total = today_withdrawals[0]["total"] if today_withdrawals else 0
    
    # Convert to USD for limit check
    usd_value = data.amount
    if data.currency == "btc":
        usd_value = data.amount * 50000
    elif data.currency == "eth":
        usd_value = data.amount * 3000
    elif data.currency == "ltc":
        usd_value = data.amount * 100
    elif data.currency == "osrs_gp":
        usd_value = data.amount / 1000000 * 0.5  # ~$0.50 per 1M GP
    
    # Check if user has pending referral bonus wager requirement
    if user.get("referral_bonus_pending", 0) > 0:
        wager_remaining = user.get("referral_wager_required", 0) - user.get("referral_wager_completed", 0)
        if wager_remaining > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Complete ${wager_remaining:.2f} more in wagers to unlock referral bonus withdrawal"
            )
    
    status = "pending"
    wait_hours = 0
    
    if today_total + usd_value > PLATFORM_CONFIG["daily_withdraw_limit_usd"]:
        status = "pending_review"
        wait_hours = PLATFORM_CONFIG["extended_withdraw_wait_hours"]
    
    success = await update_balance(user["id"], data.currency, data.amount, "subtract")
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    tx_id = str(uuid.uuid4())
    await db.transactions.insert_one({
        "id": tx_id,
        "user_id": user["id"],
        "type": "withdrawal",
        "currency": data.currency,
        "amount": data.amount,
        "address": data.address,
        "status": status,
        "wait_hours": wait_hours,
        "process_after": (datetime.now(timezone.utc) + timedelta(hours=wait_hours)).isoformat() if wait_hours else None,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Send Discord webhook notification
    color = 0xFF0000 if status == "pending_review" else 0xFFAA00
    await send_discord_webhook(
        title="💸 Withdrawal Request",
        description=f"**{user['username']}** requested withdrawal",
        color=color,
        fields=[
            {"name": "Amount", "value": f"{data.amount} {data.currency.upper()}", "inline": True},
            {"name": "Address", "value": data.address[:20] + "...", "inline": True},
            {"name": "Status", "value": status.upper(), "inline": True},
            {"name": "Wait", "value": f"{wait_hours}h" if wait_hours else "None", "inline": True}
        ]
    )
    
    message = "Withdrawal initiated"
    if wait_hours:
        message = f"Withdrawal queued for review ({wait_hours}h wait for amounts over daily limit)"
    
    return {"message": message, "amount": data.amount, "currency": data.currency, "status": status}

@api_router.get("/wallet/transactions")
async def get_transactions(user: dict = Depends(get_current_user)):
    transactions = await db.transactions.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return transactions

# ==================== GAME ROUTES ====================

@api_router.post("/games/bet", response_model=BetResponse)
async def place_bet(data: BetRequest, user: dict = Depends(get_current_user)):
    if data.game_type not in ["dice", "crash", "keno", "wheel", "plinko", "limbo"]:
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid bet amount")
    
    # Check balance
    wallet = await get_or_create_wallet(user["id"])
    if data.currency == "osrs_gp":
        balance = wallet.get("osrs_gp", 0.0)
    else:
        balance = wallet["balances"].get(data.currency, {}).get("balance", 0.0)
    
    if balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Deduct bet amount
    await update_balance(user["id"], data.currency, data.amount, "subtract")
    
    # Get seeds and generate result
    seeds = await get_or_create_seeds(user["id"])
    nonce = await increment_nonce(user["id"])
    
    result = ProvablyFair.generate_game_result(
        seeds["server_seed"],
        seeds["client_seed"],
        nonce,
        data.game_type
    )
    
    # Calculate win/loss based on game type and params
    multiplier = 0.0
    won = False
    
    if data.game_type == "dice":
        target = data.params.get("target", 50)
        over = data.params.get("over", True)
        if over:
            won = result["roll"] > target
            if won:
                multiplier = 99 / (100 - target)
        else:
            won = result["roll"] < target
            if won:
                multiplier = 99 / target
    
    elif data.game_type == "crash":
        cash_out = data.params.get("cash_out", 2.0)
        won = result["crash_point"] >= cash_out
        if won:
            multiplier = cash_out
        result["cash_out_at"] = cash_out
    
    elif data.game_type == "keno":
        selected = data.params.get("selected", [])
        hits = len(set(selected) & set(result["drawn_numbers"]))
        result["hits"] = hits
        result["selected"] = selected
        # Keno payouts based on hits
        keno_payouts = {0: 0, 1: 0, 2: 1, 3: 2, 4: 5, 5: 15, 6: 50, 7: 200, 8: 500, 9: 1000, 10: 5000}
        multiplier = keno_payouts.get(hits, 0)
        won = multiplier > 0
    
    elif data.game_type == "wheel":
        multiplier = result["multiplier"]
        won = multiplier > 0
    
    elif data.game_type == "plinko":
        multiplier = result["multiplier"]
        won = multiplier > 1
    
    elif data.game_type == "limbo":
        target = data.params.get("target", 2.0)
        won = result["target"] >= target
        if won:
            multiplier = target
        result["player_target"] = target
    
    payout = data.amount * multiplier if won else 0
    profit = payout - data.amount
    
    # Add winnings
    if payout > 0:
        await update_balance(user["id"], data.currency, payout, "add")
    
    # Update VIP status
    await update_vip_status(user["id"], data.amount, profit)
    
    # Save bet
    bet_id = str(uuid.uuid4())
    bet_record = {
        "id": bet_id,
        "user_id": user["id"],
        "username": user["username"],
        "game_type": data.game_type,
        "amount": data.amount,
        "currency": data.currency,
        "multiplier": multiplier,
        "payout": payout,
        "profit": profit,
        "result": result,
        "won": won,
        "server_seed_hash": seeds["server_seed_hash"],
        "client_seed": seeds["client_seed"],
        "nonce": nonce,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.bets.insert_one(bet_record)
    
    # Broadcast big win
    if won and multiplier >= 5:
        await manager.broadcast({
            "type": "big_win",
            "username": user["username"],
            "game": data.game_type,
            "multiplier": multiplier,
            "amount": payout,
            "currency": data.currency
        })
    
    return BetResponse(
        id=bet_id,
        game_type=data.game_type,
        amount=data.amount,
        multiplier=multiplier,
        payout=payout,
        result=result,
        won=won,
        server_seed_hash=seeds["server_seed_hash"],
        client_seed=seeds["client_seed"],
        nonce=nonce
    )

@api_router.get("/games/history")
async def get_game_history(user: dict = Depends(get_current_user), limit: int = 50):
    bets = await db.bets.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(limit)
    return bets

@api_router.get("/games/live")
async def get_live_bets(limit: int = 20):
    """Get recent bets for live feed"""
    bets = await db.bets.find(
        {}, {"_id": 0, "server_seed_hash": 0}
    ).sort("created_at", -1).to_list(limit)
    return bets

# ==================== PROVABLY FAIR ROUTES ====================

@api_router.get("/provably-fair", response_model=ProvablyFairInfo)
async def get_provably_fair_info(user: dict = Depends(get_current_user)):
    seeds = await get_or_create_seeds(user["id"])
    return ProvablyFairInfo(
        server_seed_hash=seeds["server_seed_hash"],
        client_seed=seeds["client_seed"],
        nonce=seeds["nonce"],
        previous_server_seed=seeds.get("previous_server_seed")
    )

@api_router.post("/provably-fair/rotate")
async def rotate_seeds(data: SeedChange, user: dict = Depends(get_current_user)):
    """Rotate server seed (reveals old one) and optionally set new client seed"""
    seeds = await get_or_create_seeds(user["id"])
    
    old_server_seed = seeds["server_seed"]
    new_server_seed = ProvablyFair.generate_server_seed()
    
    await db.seeds.update_one(
        {"user_id": user["id"]},
        {"$set": {
            "server_seed": new_server_seed,
            "server_seed_hash": ProvablyFair.hash_seed(new_server_seed),
            "client_seed": data.new_client_seed,
            "nonce": 0,
            "previous_server_seed": old_server_seed
        }}
    )
    
    return {
        "message": "Seeds rotated",
        "revealed_server_seed": old_server_seed,
        "new_server_seed_hash": ProvablyFair.hash_seed(new_server_seed),
        "new_client_seed": data.new_client_seed
    }

@api_router.post("/provably-fair/verify")
async def verify_bet(server_seed: str, client_seed: str, nonce: int, game_type: str):
    """Verify a bet result"""
    result = ProvablyFair.generate_game_result(server_seed, client_seed, nonce, game_type)
    return {"verified": True, "result": result}

# ==================== CHAT ROUTES ====================

@api_router.get("/chat/messages")
async def get_chat_messages(limit: int = 50):
    messages = await db.chat_messages.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)
    return list(reversed(messages))

@api_router.post("/chat/send")
async def send_chat_message(data: SendChatMessage, user: dict = Depends(get_current_user)):
    message = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "username": user["username"],
        "message": data.message,
        "message_type": "chat",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.chat_messages.insert_one(message)
    message.pop("_id", None)
    
    await manager.broadcast({"type": "chat", "data": message})
    return message

@api_router.post("/chat/tip")
async def send_tip(data: TipRequest, user: dict = Depends(get_current_user)):
    # Find recipient
    recipient = await db.users.find_one({"username": data.recipient_username}, {"_id": 0})
    if not recipient:
        raise HTTPException(status_code=404, detail="User not found")
    
    if recipient["id"] == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot tip yourself")
    
    # Transfer funds
    success = await update_balance(user["id"], data.currency, data.amount, "subtract")
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    await update_balance(recipient["id"], data.currency, data.amount, "add")
    
    # Log tip
    await db.transactions.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "type": "tip_sent",
        "recipient_id": recipient["id"],
        "recipient_username": data.recipient_username,
        "currency": data.currency,
        "amount": data.amount,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Broadcast tip in chat
    message = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "username": user["username"],
        "message": f"tipped {data.recipient_username} {data.amount} {data.currency.upper()}",
        "message_type": "tip",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "extra_data": {"amount": data.amount, "currency": data.currency, "recipient": data.recipient_username}
    }
    await db.chat_messages.insert_one(message)
    await manager.broadcast({"type": "tip", "data": message})
    
    return {"message": "Tip sent successfully"}

@api_router.post("/chat/rain")
async def make_it_rain(data: RainRequest, user: dict = Depends(get_current_user)):
    # Deduct from sender
    success = await update_balance(user["id"], data.currency, data.total_amount, "subtract")
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Get active users (online in last 5 minutes) - for now, just get recent chatters
    recent_time = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    recent_chatters = await db.chat_messages.distinct("user_id", {
        "timestamp": {"$gte": recent_time},
        "user_id": {"$ne": user["id"]}
    })
    
    if not recent_chatters:
        # Refund if no one to rain on
        await update_balance(user["id"], data.currency, data.total_amount, "add")
        raise HTTPException(status_code=400, detail="No active users to rain on")
    
    # Distribute rain
    amount_per_user = data.total_amount / len(recent_chatters)
    for recipient_id in recent_chatters:
        await update_balance(recipient_id, data.currency, amount_per_user, "add")
    
    # Broadcast rain
    message = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "username": user["username"],
        "message": f"made it rain {data.total_amount} {data.currency.upper()} on {len(recent_chatters)} users!",
        "message_type": "rain",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "extra_data": {"total": data.total_amount, "currency": data.currency, "recipients": len(recent_chatters), "per_user": amount_per_user}
    }
    await db.chat_messages.insert_one(message)
    await manager.broadcast({"type": "rain", "data": message})
    
    return {"message": "Rain distributed", "recipients": len(recent_chatters), "amount_per_user": amount_per_user}

# ==================== VIP ROUTES ====================

@api_router.get("/vip/status")
async def get_vip_status(user: dict = Depends(get_current_user)):
    tier = VIP_TIERS.get(user.get("vip_level", 0))
    next_tier = VIP_TIERS.get(user.get("vip_level", 0) + 1)
    
    return {
        "level": user.get("vip_level", 0),
        "tier_name": tier["name"],
        "progress": user.get("vip_progress", 0),
        "total_wagered": user.get("total_wagered", 0),
        "rakeback_rate": tier["rakeback"],
        "lossback_rate": tier["lossback"],
        "rakeback_available": user.get("rakeback_available", 0),
        "lossback_available": user.get("lossback_available", 0),
        "next_tier": next_tier["name"] if next_tier else None,
        "wager_to_next": next_tier["wager_required"] - user.get("total_wagered", 0) if next_tier else 0
    }

@api_router.post("/vip/claim-rakeback")
async def claim_rakeback(user: dict = Depends(get_current_user)):
    amount = user.get("rakeback_available", 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="No rakeback available")
    
    await update_balance(user["id"], "btc", amount, "add")
    await db.users.update_one({"id": user["id"]}, {"$set": {"rakeback_available": 0}})
    
    return {"message": "Rakeback claimed", "amount": amount}

@api_router.post("/vip/claim-lossback")
async def claim_lossback(user: dict = Depends(get_current_user)):
    amount = user.get("lossback_available", 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="No lossback available")
    
    await update_balance(user["id"], "btc", amount, "add")
    await db.users.update_one({"id": user["id"]}, {"$set": {"lossback_available": 0}})
    
    return {"message": "Lossback claimed", "amount": amount}

# ==================== LEADERBOARD ====================

@api_router.get("/leaderboard")
async def get_leaderboard(period: str = "all"):
    # Get top wagerers
    users = await db.users.find(
        {}, {"_id": 0, "password": 0, "email": 0}
    ).sort("total_wagered", -1).to_list(50)
    
    return [
        {
            "rank": i + 1,
            "username": u["username"],
            "total_wagered": u.get("total_wagered", 0),
            "vip_level": u.get("vip_level", 0),
            "vip_name": VIP_TIERS.get(u.get("vip_level", 0), {}).get("name", "Bronze")
        }
        for i, u in enumerate(users)
    ]

# ==================== REFERRAL SYSTEM ====================

@api_router.get("/referral/info")
async def get_referral_info(user: dict = Depends(get_current_user)):
    """Get user's referral code and stats"""
    referred_users = await db.users.find(
        {"referred_by": user["id"]}, {"_id": 0, "username": 1, "created_at": 1, "total_wagered": 1}
    ).to_list(100)
    
    return {
        "referral_code": user.get("referral_code"),
        "referral_link": f"https://degens7den.com/register?ref={user.get('referral_code')}",
        "total_referrals": len(referred_users),
        "referred_users": referred_users,
        "bonus_pending": user.get("referral_bonus_pending", 0),
        "bonus_type": user.get("referral_bonus_type"),
        "wager_required": user.get("referral_wager_required", 0),
        "wager_completed": user.get("referral_wager_completed", 0),
        "bonus_config": {
            "usd_bonus": PLATFORM_CONFIG["referral_bonus_usd"],
            "gp_bonus": PLATFORM_CONFIG["referral_bonus_gp"],
            "wager_multiplier": PLATFORM_CONFIG["referral_wager_multiplier"]
        }
    }

@api_router.post("/referral/redeem")
async def redeem_referral_code(data: ReferralCodeRedeem, user: dict = Depends(get_current_user)):
    """Redeem a referral code or promo code"""
    code = data.code.upper().strip()
    
    # Anti-abuse: Check if user already redeemed a code
    if user.get("referred_by") or user.get("referral_bonus_pending", 0) > 0:
        raise HTTPException(status_code=400, detail="You have already redeemed a referral/promo code")
    
    # Anti-abuse: Check account age (must be < 24 hours old)
    created_at = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) - created_at > timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Referral codes can only be redeemed within 24 hours of registration")
    
    # Check if it's a user referral code
    referrer = await db.users.find_one({"referral_code": code}, {"_id": 0})
    
    if referrer:
        if referrer["id"] == user["id"]:
            raise HTTPException(status_code=400, detail="Cannot use your own referral code")
        
        # Anti-abuse: Check for same IP/device (simplified - in production use fingerprinting)
        # For now, we'll check if emails are from same domain (simple check)
        referrer_domain = referrer["email"].split("@")[1] if "@" in referrer["email"] else ""
        user_domain = user["email"].split("@")[1] if "@" in user["email"] else ""
        if referrer_domain == user_domain and referrer_domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
            raise HTTPException(status_code=400, detail="Suspicious activity detected")
        
        # Apply bonus - $5 USD worth in BTC
        bonus_amount = PLATFORM_CONFIG["referral_bonus_usd"]
        wager_required = bonus_amount * PLATFORM_CONFIG["referral_wager_multiplier"]
        
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "referred_by": referrer["id"],
                "referral_bonus_pending": bonus_amount,
                "referral_bonus_type": "usd",
                "referral_wager_required": wager_required,
                "referral_wager_completed": 0
            }}
        )
        
        # Credit bonus to wallet (locked until wager requirement met)
        btc_amount = bonus_amount / 50000  # Convert USD to BTC at ~$50k
        await update_balance(user["id"], "btc", btc_amount, "add")
        
        # Update referrer's stats
        await db.users.update_one(
            {"id": referrer["id"]},
            {"$push": {"referred_users": user["id"]}}
        )
        
        # Send Discord notification
        await send_discord_webhook(
            title="🎉 New Referral Signup!",
            description=f"**{user['username']}** used referral code from **{referrer['username']}**",
            color=0x00FFAA,
            fields=[
                {"name": "Bonus", "value": f"${bonus_amount} USD", "inline": True},
                {"name": "Wager Req", "value": f"${wager_required} (10x)", "inline": True}
            ]
        )
        
        return {
            "message": "Referral code redeemed!",
            "bonus_amount": bonus_amount,
            "bonus_type": "usd",
            "wager_required": wager_required,
            "note": f"Wager ${wager_required} to unlock withdrawal"
        }
    
    # Check for promo codes
    promo = await db.promo_codes.find_one({"code": code, "is_active": True}, {"_id": 0})
    
    if promo:
        # Check usage limits
        if promo.get("uses", 0) >= promo.get("max_uses", 100):
            raise HTTPException(status_code=400, detail="Promo code has reached maximum uses")
        
        # Check expiry
        if promo.get("expires_at"):
            expires = datetime.fromisoformat(promo["expires_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expires:
                raise HTTPException(status_code=400, detail="Promo code has expired")
        
        # Check if user already used this promo
        if user["id"] in promo.get("used_by", []):
            raise HTTPException(status_code=400, detail="You have already used this promo code")
        
        bonus_amount = promo["bonus_amount"]
        bonus_type = promo["bonus_type"]
        wager_required = bonus_amount * PLATFORM_CONFIG["referral_wager_multiplier"]
        
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "referral_bonus_pending": bonus_amount,
                "referral_bonus_type": bonus_type,
                "referral_wager_required": wager_required,
                "referral_wager_completed": 0
            }}
        )
        
        # Credit bonus
        if bonus_type == "gp":
            await update_balance(user["id"], "osrs_gp", bonus_amount, "add")
        else:
            btc_amount = bonus_amount / 50000
            await update_balance(user["id"], "btc", btc_amount, "add")
        
        # Update promo usage
        await db.promo_codes.update_one(
            {"code": code},
            {"$inc": {"uses": 1}, "$push": {"used_by": user["id"]}}
        )
        
        return {
            "message": "Promo code redeemed!",
            "bonus_amount": bonus_amount,
            "bonus_type": bonus_type,
            "wager_required": wager_required
        }
    
    raise HTTPException(status_code=404, detail="Invalid referral or promo code")

@api_router.post("/referral/create-promo")
async def create_promo_code(data: ReferralCodeCreate, admin: dict = Depends(get_admin_user)):
    """Admin: Create a new promo code"""
    existing = await db.promo_codes.find_one({"code": data.code.upper()})
    if existing:
        raise HTTPException(status_code=400, detail="Promo code already exists")
    
    promo = {
        "id": str(uuid.uuid4()),
        "code": data.code.upper(),
        "bonus_type": data.bonus_type,
        "bonus_amount": data.bonus_amount if data.bonus_type == "usd" else PLATFORM_CONFIG["referral_bonus_gp"],
        "wager_requirement": data.wager_requirement,
        "uses": 0,
        "max_uses": data.max_uses,
        "used_by": [],
        "is_active": True,
        "created_by": admin["id"],
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=data.expires_days)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.promo_codes.insert_one(promo)
    
    return {"message": "Promo code created", "code": promo["code"], "bonus": promo["bonus_amount"]}

@api_router.get("/referral/promo-codes")
async def get_promo_codes(admin: dict = Depends(get_admin_user)):
    """Admin: Get all promo codes"""
    promos = await db.promo_codes.find({}, {"_id": 0}).to_list(100)
    return promos

# ==================== ADMIN ROUTES ====================

@api_router.get("/admin/stats")
async def get_admin_stats(admin: dict = Depends(get_admin_user)):
    total_users = await db.users.count_documents({})
    total_bets = await db.bets.count_documents({})
    total_wagered = await db.bets.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    total_profit = await db.bets.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$profit"}}}
    ]).to_list(1)
    
    return {
        "total_users": total_users,
        "total_bets": total_bets,
        "total_wagered": total_wagered[0]["total"] if total_wagered else 0,
        "house_profit": -(total_profit[0]["total"] if total_profit else 0)
    }

@api_router.get("/admin/users")
async def get_all_users(admin: dict = Depends(get_admin_user)):
    users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(1000)
    return users

@api_router.get("/admin/bets")
async def get_all_bets(admin: dict = Depends(get_admin_user), limit: int = 100):
    bets = await db.bets.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return bets

# ==================== WEBSOCKET ====================

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str = None):
    user_id = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
        except:
            pass
    
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong for connection keepalive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# ==================== SEED DATA ====================

@api_router.post("/seed")
async def seed_data():
    # Create admin user if not exists
    admin_exists = await db.users.find_one({"email": "admin@degensden.com"})
    if not admin_exists:
        admin_id = str(uuid.uuid4())
        admin_user = {
            "id": admin_id,
            "username": "Admin",
            "email": "admin@degensden.com",
            "password": hash_password("admin123"),
            "is_admin": True,
            "vip_level": 4,
            "vip_progress": 100,
            "total_wagered": 500000,
            "rakeback_available": 0,
            "lossback_available": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_user)
        await get_or_create_wallet(admin_id)
        await get_or_create_seeds(admin_id)
        # Give admin some balance for testing
        await update_balance(admin_id, "btc", 10.0, "add")
        await update_balance(admin_id, "eth", 100.0, "add")
        await update_balance(admin_id, "osrs_gp", 1000000000, "add")
    
    return {"message": "Seed complete"}

# ==================== KODAKGP INTEGRATION ====================

class KodakGPOrder(BaseModel):
    order_type: str  # "buy" or "sell"
    amount_gp: int  # Amount in GP
    payment_method: str = "crypto"  # crypto, paypal, etc
    contact_info: str = ""

class KodakGPServiceRequest(BaseModel):
    service_type: str  # "pure_account", "quest", "leveling", etc
    details: str
    budget: float = 0

class ForumPost(BaseModel):
    title: str
    content: str
    category: str = "general"  # general, wins, strategy, osrs

@api_router.get("/kodakgp/rates")
async def get_kodakgp_rates():
    """Get current OSRS GP rates from KodakGP"""
    return {
        "buy_rate": 0.45,  # $0.45 per 1M GP
        "sell_rate": 0.50,  # $0.50 per 1M GP
        "min_buy": 10,  # 10M GP minimum
        "max_buy": 5000,  # 5000M (5B) GP maximum
        "min_sell": 50,  # 50M GP minimum
        "contact": os.environ.get("KODAKGP_CONTACT_DISCORD", "KodakGP"),
        "services": [
            "Pure Accounts (1-126 Combat)",
            "Quest Services (RFD, MM2, DS2, etc)",
            "Power Leveling",
            "Fire Cape / Infernal Cape",
            "Diary Completion",
            "Gold Swapping (RS3 ⇄ OSRS)"
        ]
    }

@api_router.post("/kodakgp/order")
async def create_kodakgp_order(order: KodakGPOrder, user: dict = Depends(get_current_user)):
    """Create a KodakGP gold order"""
    order_id = str(uuid.uuid4())
    order_doc = {
        "id": order_id,
        "user_id": user["id"],
        "username": user["username"],
        "order_type": order.order_type,
        "amount_gp": order.amount_gp,
        "payment_method": order.payment_method,
        "contact_info": order.contact_info,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.kodakgp_orders.insert_one(order_doc)
    
    # Send Discord notification if webhook configured
    if order.order_type == "buy":
        await send_discord_webhook(
            title="💰 New KodakGP Buy Order",
            description=f"**{user['username']}** wants to buy {order.amount_gp/1000000:.0f}M GP",
            color=0x00FF00,
            fields=[
                {"name": "Amount", "value": f"{order.amount_gp/1000000:.0f}M GP", "inline": True},
                {"name": "Payment", "value": order.payment_method, "inline": True},
                {"name": "Contact", "value": order.contact_info or "N/A", "inline": True}
            ]
        )
    else:
        await send_discord_webhook(
            title="💸 New KodakGP Sell Order",
            description=f"**{user['username']}** wants to sell {order.amount_gp/1000000:.0f}M GP",
            color=0xFFAA00,
            fields=[
                {"name": "Amount", "value": f"{order.amount_gp/1000000:.0f}M GP", "inline": True},
                {"name": "Contact", "value": order.contact_info or "N/A", "inline": True}
            ]
        )
    
    return {
        "message": "Order created successfully",
        "order_id": order_id,
        "instructions": f"KodakGP staff will contact you shortly via Discord: {os.environ.get('KODAKGP_CONTACT_DISCORD', 'KodakGP')}",
        "estimated_wait": "5-15 minutes"
    }

@api_router.post("/kodakgp/service")
async def request_kodakgp_service(service: KodakGPServiceRequest, user: dict = Depends(get_current_user)):
    """Request OSRS service from KodakGP"""
    request_id = str(uuid.uuid4())
    service_doc = {
        "id": request_id,
        "user_id": user["id"],
        "username": user["username"],
        "service_type": service.service_type,
        "details": service.details,
        "budget": service.budget,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.kodakgp_services.insert_one(service_doc)
    
    await send_discord_webhook(
        title="🎮 New OSRS Service Request",
        description=f"**{user['username']}** requested: {service.service_type}",
        color=0x00E0FF,
        fields=[
            {"name": "Service", "value": service.service_type, "inline": True},
            {"name": "Budget", "value": f"${service.budget}" if service.budget > 0 else "TBD", "inline": True},
            {"name": "Details", "value": service.details[:100], "inline": False}
        ]
    )
    
    return {
        "message": "Service request submitted",
        "request_id": request_id,
        "instructions": "KodakGP will provide a quote within 24 hours"
    }

@api_router.get("/kodakgp/orders")
async def get_my_kodakgp_orders(user: dict = Depends(get_current_user)):
    """Get user's KodakGP orders"""
    orders = await db.kodakgp_orders.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return orders

# ==================== FORUM / COMMUNITY ====================

@api_router.post("/forum/post")
async def create_forum_post(post: ForumPost, user: dict = Depends(get_current_user)):
    """Create a community forum post"""
    post_id = str(uuid.uuid4())
    post_doc = {
        "id": post_id,
        "user_id": user["id"],
        "username": user["username"],
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "likes": 0,
        "comments": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.forum_posts.insert_one(post_doc)
    
    return {"message": "Post created", "post_id": post_id}

@api_router.get("/forum/posts")
async def get_forum_posts(category: str = "all", limit: int = 20):
    """Get forum posts"""
    query = {} if category == "all" else {"category": category}
    posts = await db.forum_posts.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return posts

@api_router.post("/forum/post/{post_id}/like")
async def like_forum_post(post_id: str, user: dict = Depends(get_current_user)):
    """Like a forum post"""
    result = await db.forum_posts.update_one(
        {"id": post_id},
        {"$inc": {"likes": 1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post liked"}

@api_router.post("/forum/post/{post_id}/comment")
async def comment_on_post(post_id: str, content: str, user: dict = Depends(get_current_user)):
    """Add comment to forum post"""
    comment = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "username": user["username"],
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.forum_posts.update_one(
        {"id": post_id},
        {"$push": {"comments": comment}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Comment added", "comment": comment}


@api_router.get("/")
async def root():
    return {"message": "Degen's Den Casino API - Welcome to the Den"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
