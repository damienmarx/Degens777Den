import asyncio
import uuid
import secrets
import bcrypt
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://admin:monalisa@localhost:27017/?authSource=admin')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'degensden_casino')]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

async def create_test_account():
    print("🚀 Creating universal test account...")
    
    test_user = {
        "id": str(uuid.uuid4()),
        "username": "tester",
        "email": "test@degensden.com",
        "password": hash_password("test1234"),
        "is_admin": True,
        "vip_level": 4, # Dragon tier
        "vip_progress": 100.0,
        "total_wagered": 1000000.0,
        "rakeback_available": 500.0,
        "lossback_available": 250.0,
        "referral_code": "TESTER777",
        "referred_by": None,
        "referral_bonus_pending": 0.0,
        "referral_bonus_type": None,
        "referral_wager_required": 0.0,
        "referral_wager_completed": 0.0,
        "referred_users": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Check if user already exists
    existing = await db.users.find_one({"username": "tester"})
    if existing:
        print("⚠️  Test account already exists. Updating...")
        await db.users.update_one({"username": "tester"}, {"$set": test_user})
        user_id = existing["id"]
    else:
        await db.users.insert_one(test_user)
        user_id = test_user["id"]
        print("✅ User 'tester' created.")

    # Create/Update Wallet
    wallet = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "balances": {
            "btc": {"balance": 1.5, "address": "bc1qtestaddress1234567890"},
            "eth": {"balance": 25.0, "address": "0xtestaddress1234567890"},
            "ltc": {"balance": 500.0, "address": "ltc1qtestaddress1234567890"},
            "usdc": {"balance": 50000.0, "address": "0xtestaddress1234567890"},
            "usdt": {"balance": 50000.0, "address": "0xtestaddress1234567890"}
        },
        "osrs_gp": 1000000000, # 1B GP
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    existing_wallet = await db.wallets.find_one({"user_id": user_id})
    if existing_wallet:
        await db.wallets.update_one({"user_id": user_id}, {"$set": wallet})
        print("✅ Wallet updated with 1B OSRS GP and crypto balances.")
    else:
        await db.wallets.insert_one(wallet)
        print("✅ Wallet created with 1B OSRS GP and crypto balances.")

    # Create/Update Seeds
    seeds = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "server_seed": secrets.token_hex(32),
        "server_seed_hash": secrets.token_hex(32), # Simplified for test
        "client_seed": "test_client_seed",
        "nonce": 0,
        "previous_server_seed": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    existing_seeds = await db.seeds.find_one({"user_id": user_id})
    if not existing_seeds:
        await db.seeds.insert_one(seeds)
        print("✅ Provably fair seeds initialized.")

    print("\n🎉 Test Account Ready!")
    print("----------------------")
    print("Username: tester")
    print("Email:    test@degensden.com")
    print("Password: test1234")
    print("----------------------")

if __name__ == "__main__":
    asyncio.run(create_test_account())
