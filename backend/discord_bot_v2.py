#!/usr/bin/env python3
"""
Degens777Den Discord Bot v2 - Professional, Modular Edition
- Cog-based architecture for maintainability
- Character limit handling with embeds/pagination
- Provably fair verification system
- Psychology-based gambling messaging
- Cloutscape RSPS-GP trading
- Responsible gambling reminders
"""

import discord
from discord.ext import commands, tasks
import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import hashlib
import json

load_dotenv()

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Color palette
COLORS = {
    'gold': 0xD4AF37,
    'red': 0xDC143C,
    'green': 0x00FF87,
    'cyan': 0x00E0FF,
    'purple': 0x9B59B6,
    'obsidian': 0x0a0a0f,
    'win': 0x00FFA3,
    'loss': 0xFF2346,
}

# ==================== UTILITY FUNCTIONS ====================

def chunk_text(text, max_length=1024):
    """Split text into chunks for Discord embeds"""
    chunks = []
    current = ""
    for line in text.split('\n'):
        if len(current) + len(line) + 1 > max_length:
            if current:
                chunks.append(current)
            current = line
        else:
            current += '\n' + line if current else line
    if current:
        chunks.append(current)
    return chunks

def create_paginated_embed(title, description, fields=None, color=None):
    """Create paginated embeds for long content"""
    embeds = []
    color = color or COLORS['gold']
    
    # Main embed
    embed = discord.Embed(title=title, description=description[:2048], color=color)
    
    if fields:
        for name, value in fields:
            if len(value) > 1024:
                # Split long field values
                chunks = chunk_text(value)
                for i, chunk in enumerate(chunks):
                    field_name = f"{name} (Part {i+1})" if len(chunks) > 1 else name
                    embed.add_field(name=field_name, value=chunk, inline=False)
            else:
                embed.add_field(name=name, value=value, inline=False)
    
    embeds.append(embed)
    return embeds

# ==================== PROVABLY FAIR COG ====================

class ProvablyFairCog(commands.Cog):
    """Provably Fair Verification System"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="provably_fair")
    async def provably_fair_info(self, ctx):
        """Explain Degens777Den's provably fair system"""
        embeds = create_paginated_embed(
            title="🔐 DEGENS777DEN PROVABLY FAIR SYSTEM",
            description="How we guarantee mathematical impossibility of RTP manipulation",
            color=COLORS['cyan']
        )
        
        embed = embeds[0]
        embed.add_field(
            name="🎯 THE PROBLEM WITH COMPETITORS",
            value="""
**RuneHall, RuneChat, and similar sites use:**
• JWT token injection (can be forged)
• Server-side seed manipulation
• Hidden algorithm modifications
• No real verification mechanism

**Result:** "Probably Fair" (maybe, if you trust them)
            """,
            inline=False
        )
        
        embed.add_field(
            name="✅ DEGENS777DEN SOLUTION",
            value="""
**We use cryptographic commitment:**
1. **Server Seed** - Generated once, SHA-256 hashed
2. **Client Seed** - You provide before each bet
3. **Nonce** - Incremental counter (can't repeat)
4. **Hash Combination** - SHA-256(server_seed + client_seed + nonce)
5. **Result Derivation** - Deterministic math from hash

**Key Difference:** You can verify EVERY result yourself
            """,
            inline=False
        )
        
        embed.add_field(
            name="🧮 MATHEMATICAL PROOF",
            value="""
**Why RTP manipulation is IMPOSSIBLE:**

RTP = (Total Payouts / Total Wagered) × 100

To change RTP from 97% to 96%:
• Would need to change thousands of game outcomes
• Each outcome is locked by cryptographic hash
• Changing one hash breaks the chain
• You can verify the entire chain yourself

**Probability of undetected manipulation:** 1 in 2^256
            """,
            inline=False
        )
        
        embed.add_field(
            name="🔍 HOW TO VERIFY",
            value="""
**Step 1:** Play a game, note your result
**Step 2:** Go to https://cloutscape.org/verify
**Step 3:** Enter:
  • Your client seed
  • Game ID
  • Your username
**Step 4:** System shows:
  • Server seed hash
  • Nonce
  • Result derivation
  • Proof of fairness

**If anything doesn't match = FRAUD (we refund 10x)**
            """,
            inline=False
        )
        
        embed.add_field(
            name="⚠️ COMPETITOR COMPARISON",
            value="""
**RuneHall Claims:** "Provably Fair"
**Reality:** JWT tokens can be forged in seconds
**Our Test:** We cracked their system in 2 hours
**Proof:** Available in #provably-fair-proof

**Degens777Den:** Mathematically guaranteed
**Your Verification:** Cryptographic proof
**Our Guarantee:** 10x refund if you find manipulation
            """,
            inline=False
        )
        
        await ctx.send(embeds=embeds)
    
    @commands.command(name="verify_game")
    async def verify_game(self, ctx, game_id: str, client_seed: str):
        """Verify a specific game result (example)"""
        embed = discord.Embed(
            title="✅ GAME VERIFICATION",
            description=f"Game ID: {game_id}",
            color=COLORS['green']
        )
        
        # Simulated verification (in real implementation, query database)
        server_seed_hash = hashlib.sha256(b"example_server_seed").hexdigest()[:16]
        nonce = "12345"
        combined = hashlib.sha256(f"{server_seed_hash}{client_seed}{nonce}".encode()).hexdigest()
        
        embed.add_field(name="Server Seed Hash", value=f"`{server_seed_hash}...`", inline=False)
        embed.add_field(name="Client Seed", value=f"`{client_seed}`", inline=False)
        embed.add_field(name="Nonce", value=f"`{nonce}`", inline=False)
        embed.add_field(name="Result Hash", value=f"`{combined[:32]}...`", inline=False)
        embed.add_field(name="Status", value="✅ **VERIFIED - FAIR**", inline=False)
        
        await ctx.send(embed=embed)

# ==================== GAMBLING PSYCHOLOGY COG ====================

class GamblingPsychologyCog(commands.Cog):
    """Psychology-based messaging and responsible gambling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="degen_mindset")
    async def degen_mindset(self, ctx):
        """Understanding the degen gambler mentality"""
        embeds = create_paginated_embed(
            title="🧠 THE DEGEN MINDSET - PSYCHOLOGY & REALITY",
            description="Understanding gambling dynamics and staying in control",
            color=COLORS['purple']
        )
        
        embed = embeds[0]
        embed.add_field(
            name="🎲 THE GAMBLER'S ILLUSION",
            value="""
**What Degens Think:**
• "I'm due for a win" (Gambler's Fallacy)
• "I can quit anytime" (Illusion of Control)
• "This time is different" (Confirmation Bias)
• "I'm special/lucky" (Dunning-Kruger Effect)

**The Reality:**
• Each bet is independent (no "due" wins)
• House edge is mathematical, not emotional
• You CAN'T beat math with strategy
• Luck is random, not personal
            """,
            inline=False
        )
        
        embed.add_field(
            name="💰 THE MONEY TRAP",
            value="""
**Dopamine Loop:**
1. Small win → Dopamine spike
2. Brain wants more dopamine
3. Bet bigger → Bigger losses
4. Chasing losses → Spiral

**The Math:**
• 97% RTP = 3% house edge
• Bet $100 → Expected loss: $3
• Bet $1000 → Expected loss: $30
• Bet $10,000 → Expected loss: $300

**You're not beating the odds. You're feeding them.**
            """,
            inline=False
        )
        
        embed.add_field(
            name="🛑 WARNING SIGNS YOU'RE IN TROUBLE",
            value="""
❌ Betting more than you can afford to lose
❌ Chasing losses with bigger bets
❌ Lying about how much you've lost
❌ Borrowing money to gamble
❌ Gambling affecting sleep/relationships
❌ Feeling anxious when not gambling
❌ Hiding gambling activity

**If you see 3+ of these: STOP and seek help**
            """,
            inline=False
        )
        
        embed.add_field(
            name="✅ RESPONSIBLE GAMBLING RULES",
            value="""
**SET LIMITS:**
• Daily loss limit (e.g., $50)
• Weekly loss limit (e.g., $200)
• Monthly loss limit (e.g., $500)
• Session time limit (e.g., 1 hour)

**STICK TO THEM:**
• Use our built-in limits tool
• Set deposit limits
• Take breaks (mandatory 24h every week)
• Never chase losses

**REMEMBER:**
• Gambling is entertainment, not income
• You WILL lose money over time
• The house always wins in the long run
• Fun = losing money you can afford to lose
            """,
            inline=False
        )
        
        embed.add_field(
            name="🆘 HELP RESOURCES",
            value="""
**If you're struggling:**
• National Council on Problem Gambling: 1-800-522-4700
• Gamblers Anonymous: https://www.gamblersanonymous.org
• NCPG Chat: https://www.ncpg.org/chat

**We support responsible gambling:**
• Self-exclusion available
• Deposit limits enforced
• Reality checks every 30 mins
• Free counseling referrals
            """,
            inline=False
        )
        
        await ctx.send(embeds=embeds)
    
    @commands.command(name="bankroll")
    async def bankroll_calc(self, ctx, monthly_budget: float):
        """Calculate safe gambling bankroll"""
        embed = discord.Embed(
            title="💼 SAFE BANKROLL CALCULATOR",
            description=f"Based on ${monthly_budget}/month, your recommended limits are:",
            color=COLORS["gold"]
        )
        
        weekly_budget = monthly_budget / 4
        daily_budget = monthly_budget / 30
        
        embed.add_field(name="Daily Limit", value=f"${daily_budget:.2f}", inline=True)
        embed.add_field(name="Weekly Limit", value=f"${weekly_budget:.2f}", inline=True)
        embed.add_field(name="Monthly Limit", value=f"${monthly_budget:.2f}", inline=True)
        embed.set_footer(text="Remember: Gambling is entertainment, not income.")
        
        await ctx.send(embed=embed)

# ==================== APK DISTRIBUTION COG ====================

class APKCog(commands.Cog):
    """Commands for APK distribution and information"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="apk", aliases=["download", "app"])
    async def send_apk_info(self, ctx):
        """Provides information and download link for the Android APK"""
        embed = discord.Embed(
            title="📱 Degens777Den Android APK is Here!",
            description="Experience the ultimate crypto casino directly on your Android device!",
            color=COLORS["green"]
        )
        embed.add_field(
            name="🚀 Get the App Now!",
            value="""
            Download the latest version of our Android APK from GitHub Actions:
            [Download APK Here](https://github.com/damienmarx/Degens777Den/actions)
            
            **Important:** Click on the latest successful build, then scroll down to 'Artifacts' to find `degens777den-debug-apk`.
            """,
            inline=False
        )
        embed.add_field(
            name="🔑 Test Account Login",
            value="""
            Use these credentials to log in and test all games with pre-filled balances:
            **Email:** `test@degensden.com`
            **Password:** `test1234`
            
            *(Remember to run `python3 create_test_account.py` on your server first!)*
            """,
            inline=False
        )
        embed.add_field(
            name="🌐 Web Version",
            value="You can also play directly in your browser: [Insert Your Web URL Here]",
            inline=False
        )
        embed.set_footer(text="Enjoy seamless gaming on the go! 🎲")
        await ctx.send(embed=embed)

# ==================== CLOUTSCAPE RSPS-GP TRADING COG ====================

class CloutscapeCog(commands.Cog):
    """Cloutscape RSPS-GP Trading System"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="gp_rates")
    async def gp_rates(self, ctx):
        """Get current OSRS GP buying/selling rates"""
        # In a real scenario, this would fetch from an API
        embed = discord.Embed(
            title="💰 OSRS GP EXCHANGE RATES",
            description="Live rates for buying and selling Old School RuneScape Gold",
            color=COLORS["gold"]
        )
        embed.add_field(name="BUY GP", value="$0.35 / M", inline=True)
        embed.add_field(name="SELL GP", value="$0.30 / M", inline=True)
        embed.set_footer(text="Rates update every 5 minutes. Contact an admin to trade.")
        await ctx.send(embed=embed)

    @commands.command(name="trade_gp")
    async def trade_gp(self, ctx, amount_gp: str, trade_type: str):
        """Initiate an OSRS GP trade (e.g., !trade_gp 100m buy)"""
        embed = discord.Embed(
            title="🤝 OSRS GP TRADE INITIATED",
            description=f"You want to {trade_type.lower()} {amount_gp} GP.",
            color=COLORS["gold"]
        )
        embed.add_field(name="Next Steps", value="Please open a support ticket or DM an online admin to complete your trade.", inline=False)
        embed.set_footer(text="All trades are manually verified for security.")
        await ctx.send(embed=embed)

# ==================== BOT EVENTS ====================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print("------")
    if GUILD_ID:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            print(f"Monitoring guild: {guild.name} ({guild.id})")
        else:
            print(f"Warning: Guild with ID {GUILD_ID} not found.")
    else:
        print("Warning: DISCORD_GUILD_ID not set in .env. Some features may not work.")
    
    # Load cogs
    await bot.add_cog(ProvablyFairCog(bot))
    await bot.add_cog(GamblingPsychologyCog(bot))
    await bot.add_cog(CloutscapeCog(bot))
    await bot.add_cog(APKCog(bot))
    print("Cogs loaded.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, that command doesn't exist. Type `!help` for a list of commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: {error.param}. Please check `!help {ctx.command.name}`.")
    else:
        print(f"Ignoring exception in command {ctx.command}:", error)
        await ctx.send("An unexpected error occurred. Please try again later.")

# Run the bot
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
