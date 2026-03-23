#!/usr/bin/env python3
"""
Degen's Den Casino - Discord Bot
Extensive bot for server setup, notifications, and community management
"""

import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import aiohttp
from datetime import datetime, timezone
from dotenv import load_dotenv
import json

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "degensden_casino")

# MongoDB Connection
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Bot Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Initialize Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== CHANNEL CONFIGURATION ====================

CHANNEL_CONFIG = {
    "announcements": {
        "name": "announcements",
        "topic": "Official Degen's Den Casino announcements and updates",
        "category": "DEGEN'S DEN",
        "type": "text"
    },
    "welcome": {
        "name": "welcome",
        "topic": "Welcome to Degen's Den! Read the rules and get started.",
        "category": "DEGEN'S DEN",
        "type": "text"
    },
    "rules": {
        "name": "rules",
        "topic": "Server rules and guidelines",
        "category": "DEGEN'S DEN",
        "type": "text"
    },
    "general": {
        "name": "general-chat",
        "topic": "General discussion for degens",
        "category": "COMMUNITY",
        "type": "text"
    },
    "gambling": {
        "name": "gambling-talk",
        "topic": "Discuss strategies, wins, and losses",
        "category": "COMMUNITY",
        "type": "text"
    },
    "osrs": {
        "name": "osrs-chat",
        "topic": "OSRS discussions, GP trades, and game talk",
        "category": "COMMUNITY",
        "type": "text"
    },
    "crypto": {
        "name": "crypto-chat",
        "topic": "Crypto discussions, market talk, and degen trades",
        "category": "COMMUNITY",
        "type": "text"
    },
    "wins": {
        "name": "big-wins",
        "topic": "Share your epic wins! Automated big win notifications.",
        "category": "CASINO",
        "type": "text"
    },
    "deposits": {
        "name": "deposit-notifications",
        "topic": "Deposit confirmations (staff only view)",
        "category": "CASINO",
        "type": "text"
    },
    "withdrawals": {
        "name": "withdrawal-requests",
        "topic": "Withdrawal processing (staff only)",
        "category": "CASINO",
        "type": "text"
    },
    "referrals": {
        "name": "refer-a-degen",
        "topic": "Get your referral code and earn rewards!",
        "category": "BONUSES",
        "type": "text"
    },
    "promos": {
        "name": "promo-codes",
        "topic": "Active promo codes and bonuses",
        "category": "BONUSES",
        "type": "text"
    },
    "vip": {
        "name": "vip-lounge",
        "topic": "Exclusive VIP member area",
        "category": "VIP",
        "type": "text"
    },
    "support": {
        "name": "support",
        "topic": "Get help from our team",
        "category": "SUPPORT",
        "type": "text"
    },
    "tickets": {
        "name": "open-ticket",
        "topic": "Create a support ticket",
        "category": "SUPPORT",
        "type": "text"
    },
    "voice": {
        "name": "Degen Voice",
        "category": "COMMUNITY",
        "type": "voice"
    }
}

# ==================== EMBED TEMPLATES ====================

def create_welcome_embed():
    embed = discord.Embed(
        title="Welcome to Degen's Den Casino!",
        description="The #1 Crypto & OSRS Casino for true degens!",
        color=0xE0FF00
    )
    embed.add_field(
        name="What We Offer",
        value="""
**Games:**  Dice, Keno, Crash, Lucky Wheel, Plinko, Limbo

**Currencies:** BTC, ETH, LTC, USDC, USDT + OSRS GP

**Features:**
- Provably Fair (verify every bet)
- VIP Program with Rakeback & Lossback
- Rain & Tips in chat
- Fast withdrawals
        """,
        inline=False
    )
    embed.add_field(
        name="Get Started",
        value="1. Visit https://degens7den.com\n2. Create an account\n3. Use a referral code for $5 FREE bonus!\n4. Deposit and start winning!",
        inline=False
    )
    embed.set_thumbnail(url="https://i.imgur.com/degen_logo.png")  # Replace with actual logo
    embed.set_footer(text="Gamble responsibly | 18+ only")
    return embed

def create_rules_embed():
    embed = discord.Embed(
        title="Server Rules",
        description="Follow these rules to keep the Den clean!",
        color=0xFF2346
    )
    embed.add_field(
        name="1. Be Respectful",
        value="No harassment, hate speech, or personal attacks.",
        inline=False
    )
    embed.add_field(
        name="2. No Spam",
        value="No excessive messages, caps, or promotional spam.",
        inline=False
    )
    embed.add_field(
        name="3. No Begging",
        value="Don't beg for tips, rain, or free money.",
        inline=False
    )
    embed.add_field(
        name="4. No Scamming",
        value="Any scam attempts = permanent ban.",
        inline=False
    )
    embed.add_field(
        name="5. English Only",
        value="Keep conversations in English for moderation.",
        inline=False
    )
    embed.add_field(
        name="6. 18+ Only",
        value="You must be of legal gambling age in your jurisdiction.",
        inline=False
    )
    embed.set_footer(text="Breaking rules = warn/mute/ban at staff discretion")
    return embed

def create_referral_embed():
    embed = discord.Embed(
        title="Refer a Degen - Earn Rewards!",
        description="Share your referral code and both you and your friend get bonuses!",
        color=0x00FFA3
    )
    embed.add_field(
        name="Your Bonus",
        value="Get 10% of your referral's wagers as rakeback FOREVER!",
        inline=True
    )
    embed.add_field(
        name="Friend's Bonus",
        value="$5 FREE or 35M OSRS GP on signup!",
        inline=True
    )
    embed.add_field(
        name="How It Works",
        value="""
1. Get your unique referral code from the website
2. Share it with friends
3. They sign up and enter your code
4. Both of you get rewarded!

**Wager Requirement:** 10x the bonus amount before withdrawal
        """,
        inline=False
    )
    embed.add_field(
        name="Get Your Code",
        value="Visit https://degens7den.com/referral",
        inline=False
    )
    return embed

def create_promo_embed(promos):
    embed = discord.Embed(
        title="Active Promo Codes",
        description="Enter these codes on the website to claim your bonus!",
        color=0xE0FF00
    )
    
    if promos:
        for promo in promos[:5]:  # Show up to 5 promos
            uses_left = promo.get("max_uses", 100) - promo.get("uses", 0)
            bonus_text = f"${promo['bonus_amount']}" if promo['bonus_type'] == 'usd' else f"{promo['bonus_amount']/1000000:.0f}M GP"
            embed.add_field(
                name=f"`{promo['code']}`",
                value=f"Bonus: {bonus_text}\nUses Left: {uses_left}",
                inline=True
            )
    else:
        embed.add_field(
            name="No Active Promos",
            value="Check back later for new codes!",
            inline=False
        )
    
    embed.set_footer(text="Promos have 10x wager requirement | New users only")
    return embed

def create_vip_embed():
    embed = discord.Embed(
        title="VIP Program",
        description="Level up and earn more rewards!",
        color=0xFFD700
    )
    
    tiers = [
        ("Bronze", "$0", "5% Rakeback", "0% Lossback"),
        ("Silver", "$1,000", "10% Rakeback", "2% Lossback"),
        ("Gold", "$10,000", "15% Rakeback", "5% Lossback"),
        ("Platinum", "$50,000", "20% Rakeback", "8% Lossback"),
        ("Dragon", "$250,000", "30% Rakeback", "12% Lossback"),
    ]
    
    for tier, wager, rakeback, lossback in tiers:
        embed.add_field(
            name=f"{tier}",
            value=f"Wager: {wager}\n{rakeback}\n{lossback}",
            inline=True
        )
    
    embed.set_footer(text="Wager more to level up! Check /vip for your progress")
    return embed

# ==================== BOT EVENTS ====================

@bot.event
async def on_ready():
    print(f"Degen's Den Bot is online! Logged in as {bot.user}")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Start background tasks
    update_stats.start()

@bot.event
async def on_member_join(member):
    """Send welcome DM and assign role"""
    try:
        welcome_embed = create_welcome_embed()
        welcome_embed.description = f"Welcome to the Den, {member.mention}!"
        await member.send(embed=welcome_embed)
    except:
        pass  # DMs might be disabled

# ==================== SLASH COMMANDS ====================

@bot.tree.command(name="setup", description="[Admin] Setup the entire Discord server for Degen's Den")
@app_commands.default_permissions(administrator=True)
async def setup_server(interaction: discord.Interaction):
    """Setup the entire Discord server with channels and content"""
    await interaction.response.defer(ephemeral=True)
    
    guild = interaction.guild
    created_channels = []
    
    # Create categories
    categories = {}
    category_names = set(ch["category"] for ch in CHANNEL_CONFIG.values())
    
    for cat_name in category_names:
        existing = discord.utils.get(guild.categories, name=cat_name)
        if not existing:
            existing = await guild.create_category(cat_name)
        categories[cat_name] = existing
    
    # Create channels
    for key, config in CHANNEL_CONFIG.items():
        category = categories[config["category"]]
        existing = discord.utils.get(guild.channels, name=config["name"])
        
        if not existing:
            if config["type"] == "voice":
                channel = await guild.create_voice_channel(
                    config["name"],
                    category=category
                )
            else:
                channel = await guild.create_text_channel(
                    config["name"],
                    category=category,
                    topic=config.get("topic", "")
                )
            created_channels.append(channel.name)
    
    # Populate channels with content
    await populate_channels(guild)
    
    await interaction.followup.send(
        f"Server setup complete!\n"
        f"Created {len(created_channels)} channels: {', '.join(created_channels)}\n"
        f"Populated all channels with Degen's Den content!",
        ephemeral=True
    )

async def populate_channels(guild):
    """Fill channels with appropriate content"""
    
    # Welcome channel
    welcome_ch = discord.utils.get(guild.channels, name="welcome")
    if welcome_ch:
        await welcome_ch.purge(limit=10)
        await welcome_ch.send(embed=create_welcome_embed())
    
    # Rules channel
    rules_ch = discord.utils.get(guild.channels, name="rules")
    if rules_ch:
        await rules_ch.purge(limit=10)
        await rules_ch.send(embed=create_rules_embed())
    
    # Referral channel
    ref_ch = discord.utils.get(guild.channels, name="refer-a-degen")
    if ref_ch:
        await ref_ch.purge(limit=10)
        await ref_ch.send(embed=create_referral_embed())
    
    # VIP channel
    vip_ch = discord.utils.get(guild.channels, name="vip-lounge")
    if vip_ch:
        await vip_ch.purge(limit=10)
        await vip_ch.send(embed=create_vip_embed())
    
    # Promo channel
    promo_ch = discord.utils.get(guild.channels, name="promo-codes")
    if promo_ch:
        await promo_ch.purge(limit=10)
        promos = await db.promo_codes.find({"is_active": True}, {"_id": 0}).to_list(10)
        await promo_ch.send(embed=create_promo_embed(promos))
    
    # Announcements
    ann_ch = discord.utils.get(guild.channels, name="announcements")
    if ann_ch:
        embed = discord.Embed(
            title="Welcome to Degen's Den Casino!",
            description="We're live! Start playing at https://degens7den.com",
            color=0xE0FF00
        )
        embed.add_field(name="Launch Bonus", value="Use code `LAUNCH` for $10 FREE!", inline=False)
        await ann_ch.send(embed=embed)

@bot.tree.command(name="stats", description="View casino statistics")
async def casino_stats(interaction: discord.Interaction):
    """Show casino statistics"""
    await interaction.response.defer()
    
    total_users = await db.users.count_documents({})
    total_bets = await db.bets.count_documents({})
    total_wagered = await db.bets.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    wagered = total_wagered[0]["total"] if total_wagered else 0
    
    embed = discord.Embed(
        title="Degen's Den Statistics",
        color=0xE0FF00
    )
    embed.add_field(name="Total Users", value=f"{total_users:,}", inline=True)
    embed.add_field(name="Total Bets", value=f"{total_bets:,}", inline=True)
    embed.add_field(name="Total Wagered", value=f"${wagered:,.2f}", inline=True)
    embed.set_footer(text="Updated in real-time")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="referral", description="Get your referral link")
async def get_referral(interaction: discord.Interaction):
    """Get referral information"""
    embed = create_referral_embed()
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="vip", description="View VIP program details")
async def vip_info(interaction: discord.Interaction):
    """Show VIP program info"""
    embed = create_vip_embed()
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="promo", description="View active promo codes")
async def promo_codes(interaction: discord.Interaction):
    """Show active promo codes"""
    promos = await db.promo_codes.find({"is_active": True}, {"_id": 0}).to_list(10)
    embed = create_promo_embed(promos)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="View top wagerers")
async def leaderboard(interaction: discord.Interaction):
    """Show top wagerers"""
    await interaction.response.defer()
    
    users = await db.users.find(
        {}, {"_id": 0, "username": 1, "total_wagered": 1, "vip_level": 1}
    ).sort("total_wagered", -1).limit(10).to_list(10)
    
    embed = discord.Embed(
        title="Top 10 Degens",
        description="The biggest wagerers on Degen's Den!",
        color=0xFFD700
    )
    
    medals = ["", "", "", "", "", "", "", "", "", ""]
    
    for i, user in enumerate(users):
        embed.add_field(
            name=f"{medals[i]} #{i+1} - {user['username']}",
            value=f"Wagered: ${user.get('total_wagered', 0):,.2f}",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="createpromo", description="[Admin] Create a new promo code")
@app_commands.default_permissions(administrator=True)
async def create_promo(
    interaction: discord.Interaction,
    code: str,
    bonus_usd: float = 5.0,
    max_uses: int = 100,
    expires_days: int = 30
):
    """Create a new promo code"""
    existing = await db.promo_codes.find_one({"code": code.upper()})
    if existing:
        await interaction.response.send_message("Promo code already exists!", ephemeral=True)
        return
    
    promo = {
        "id": str(interaction.id),
        "code": code.upper(),
        "bonus_type": "usd",
        "bonus_amount": bonus_usd,
        "wager_requirement": 10.0,
        "uses": 0,
        "max_uses": max_uses,
        "used_by": [],
        "is_active": True,
        "created_by": str(interaction.user.id),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.promo_codes.insert_one(promo)
    
    embed = discord.Embed(
        title="Promo Code Created!",
        description=f"Code: `{code.upper()}`",
        color=0x00FF00
    )
    embed.add_field(name="Bonus", value=f"${bonus_usd}", inline=True)
    embed.add_field(name="Max Uses", value=str(max_uses), inline=True)
    embed.add_field(name="Expires", value=f"{expires_days} days", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Also post in promo channel
    promo_ch = discord.utils.get(interaction.guild.channels, name="promo-codes")
    if promo_ch:
        public_embed = discord.Embed(
            title="New Promo Code!",
            description=f"Use code `{code.upper()}` for ${bonus_usd} FREE bonus!",
            color=0xE0FF00
        )
        public_embed.set_footer(text="10x wager requirement | New users only")
        await promo_ch.send(embed=public_embed)

@bot.tree.command(name="announce", description="[Admin] Make an announcement")
@app_commands.default_permissions(administrator=True)
async def announce(
    interaction: discord.Interaction,
    title: str,
    message: str,
    ping_everyone: bool = False
):
    """Make an announcement"""
    ann_ch = discord.utils.get(interaction.guild.channels, name="announcements")
    if not ann_ch:
        await interaction.response.send_message("Announcements channel not found!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=title,
        description=message,
        color=0xE0FF00,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text=f"Announced by {interaction.user.name}")
    
    content = "@everyone" if ping_everyone else None
    await ann_ch.send(content=content, embed=embed)
    await interaction.response.send_message("Announcement sent!", ephemeral=True)

@bot.tree.command(name="bigwin", description="[Admin] Announce a big win")
@app_commands.default_permissions(administrator=True)
async def big_win_announce(
    interaction: discord.Interaction,
    username: str,
    game: str,
    multiplier: float,
    amount: float,
    currency: str = "BTC"
):
    """Announce a big win"""
    wins_ch = discord.utils.get(interaction.guild.channels, name="big-wins")
    if not wins_ch:
        await interaction.response.send_message("Big wins channel not found!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="MASSIVE WIN!",
        description=f"**{username}** just hit big on **{game}**!",
        color=0x00FF00
    )
    embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
    embed.add_field(name="Payout", value=f"{amount} {currency}", inline=True)
    embed.set_footer(text="Play at degens7den.com")
    
    await wins_ch.send(embed=embed)
    await interaction.response.send_message("Big win announced!", ephemeral=True)

# ==================== BACKGROUND TASKS ====================

@tasks.loop(minutes=30)
async def update_stats():
    """Periodically update promo codes in the promo channel"""
    for guild in bot.guilds:
        promo_ch = discord.utils.get(guild.channels, name="promo-codes")
        if promo_ch:
            promos = await db.promo_codes.find({"is_active": True}, {"_id": 0}).to_list(10)
            
            # Find and update the promo message
            async for message in promo_ch.history(limit=5):
                if message.author == bot.user and message.embeds:
                    await message.edit(embed=create_promo_embed(promos))
                    break

# ==================== PREFIX COMMANDS (LEGACY) ====================

@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.command(name="help")
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="Degen's Den Bot Commands",
        color=0xE0FF00
    )
    embed.add_field(
        name="Slash Commands",
        value="""
`/stats` - View casino statistics
`/referral` - Get referral info
`/vip` - View VIP program
`/promo` - View active promos
`/leaderboard` - Top wagerers
        """,
        inline=False
    )
    embed.add_field(
        name="Admin Commands",
        value="""
`/setup` - Setup server channels
`/createpromo` - Create promo code
`/announce` - Make announcement
`/bigwin` - Announce a big win
        """,
        inline=False
    )
    await ctx.send(embed=embed)

# ==================== RUN BOT ====================

if __name__ == "__main__":
    from datetime import timedelta
    
    if not BOT_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not set in environment!")
        print("Set it in backend/.env and restart the bot.")
    else:
        bot.run(BOT_TOKEN)
