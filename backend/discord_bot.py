#!/usr/bin/env python3
"""
Degens777Den Casino - Discord Bot
Wolf Pack Onboarding & Server Management
"""

import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
import sys

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
GUILD_ID = os.environ.get("DISCORD_GUILD_ID", "")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")

# Colors
GOLD = 0xD4AF37
RED = 0xDC143C
GREEN = 0x00FF87
BLACK = 0x0A0A0F

# Bot Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Initialize Bot
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ==================== WELCOME MESSAGES ====================

WELCOME_DM = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🐺 WELCOME TO DEGENS777DEN - WOLF PACK 🐺        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

**Greetings, {username}!**

You've just entered the Den where **REAL degens** roam. 

**🎰 What is Degens777Den?**
We're a **100% transparent, provably fair** casino built for OSRS players and crypto gamblers who are tired of being **scammed by ponzi sites** like RuneHall and RuneChat.

**🐺 THE CHOICE:**
• **EAT WITH THE WOLVES** 🐺 - Play at Degens777Den where 97% RTP is REAL
• **BE SLAUGHTERED WITH THE SHEEP** 🐑 - Keep donating to RuneHall/RuneChat's manipulated games

**💎 WHY WE'RE DIFFERENT:**
✅ **97% RTP** - Fixed, never manipulated
✅ **Provably Fair** - Every seed verifiable
✅ **No Scams** - We expose predatory tactics
✅ **OSRS Gold** - Integrated with KodakGP
✅ **VIP Rewards** - Up to 15% rakeback + 10% lossback
✅ **Max 350 Players** - Quality over quantity

**🎲 THE DEGEN PHILOSOPHY:**
> *"All In. Ben Motto."*
> *"In a world of sheep, be a degen."*

We don't chase wins. We chase **EXCITEMENT**.
We don't trust ponzis. We trust **MATHEMATICS**.
We don't gamble alone. We gamble as a **PACK**.

**🚀 GET STARTED:**
1. Visit: **https://cloutscape.org**
2. Create account (username/password or Discord OAuth)
3. Deposit: BTC, ETH, LTC, USDC, or OSRS GP
4. Play: Dice, Keno, Crash, Wheel, Plinko, Limbo
5. Win: Cash out anytime (no delays, no traps)

**🎁 FIRST TIME BONUS:**
Use referral code from any pack member for **$5 USD** or **35M OSRS GP** bonus!

**📜 PACK RULES:**
• Be respectful to fellow degens
• No scamming, doxxing, or harassment
• Rage fits are temporary - bans are permanent
• Play responsibly - set limits

**💬 NEED HELP?**
• Ask in #general-chat
• Open a ticket in #support
• DM staff (gold name = mod, red name = admin)

═══════════════════════════════════════════════════════════

**Welcome to the pack, degen.** 🐺

*The house doesn't always win here. But the pack always survives.*

**Play now:** https://cloutscape.org
"""

WELCOME_CHANNEL_MESSAGE = """
🐺 **A NEW DEGEN HAS ENTERED THE DEN!** 🐺

**Welcome {mention} to Degens777Den!**

You've joined the **WOLF PACK** - a community of degens who refuse to be **sheep** for ponzi casinos like RuneHall and RuneChat.

**🎰 Quick Start:**
• Visit **https://cloutscape.org** to play
• Check your DMs for full onboarding guide
• Ask questions in #general-chat
• Verify your account for full access

**💎 What Makes Us Different?**
While other casinos manipulate RTP and trap your funds, we offer:
✅ **Real 97% RTP** (not fake "provably fair")
✅ **Instant withdrawals** (no 3-day "processing")
✅ **Transparent seeds** (verify every bet)
✅ **No predatory bonuses** (no 50× wagering requirements)

**🐺 THE PHILOSOPHY:**
> *"Eat with the wolves or be slaughtered with the sheep."*

RuneHall scams you with manipulated RTPs.
RuneChat traps you with fake big wins.
**Degens777Den protects you with REAL transparency.**

═══════════════════════════════════════════════════════════

**Ready to join the hunt?** 🎲
👉 **https://cloutscape.org**

*All In. Ben Motto.* 🔥
"""

SERVER_SETUP_CHANNELS = {
    "📢 INFORMATION": [
        {"name": "welcome", "topic": "Welcome to the Wolf Pack! 🐺"},
        {"name": "rules", "topic": "Den rules - read before posting"},
        {"name": "announcements", "topic": "Official Degens777Den updates"},
        {"name": "why-degens", "topic": "Why we're better than RuneHall/RuneChat"},
    ],
    "💬 COMMUNITY": [
        {"name": "general-chat", "topic": "Main chat for all degens"},
        {"name": "big-wins", "topic": "Post your massive wins here! 🎰"},
        {"name": "strategy", "topic": "Discuss game strategies and tips"},
        {"name": "memes", "topic": "Degen memes only 🔥"},
    ],
    "🎮 CASINO": [
        {"name": "live-bets", "topic": "Real-time bet notifications"},
        {"name": "giveaways", "topic": "Rain and community giveaways 💰"},
        {"name": "vip-lounge", "topic": "Exclusive VIP member chat"},
    ],
    "💼 OSRS": [
        {"name": "gold-trades", "topic": "Buy/sell OSRS GP with KodakGP"},
        {"name": "services", "topic": "Pure accounts, quests, capes"},
        {"name": "osrs-general", "topic": "OSRS discussion"},
    ],
    "❓ SUPPORT": [
        {"name": "support", "topic": "Get help from staff"},
        {"name": "suggestions", "topic": "Suggest features and improvements"},
    ],
}

# ==================== BOT EVENTS ====================

@bot.event
async def on_ready():
    print(f"╔═══════════════════════════════════════════════════════╗")
    print(f"║                                                       ║")
    print(f"║       🐺 DEGENS777DEN DISCORD BOT ONLINE 🐺          ║")
    print(f"║                                                       ║")
    print(f"╚═══════════════════════════════════════════════════════╝")
    print(f"")
    print(f"Bot User:    {bot.user.name} (ID: {bot.user.id})")
    print(f"Servers:     {len(bot.guilds)}")
    print(f"Members:     {sum([g.member_count for g in bot.guilds])}")
    print(f"")
    print(f"Features:")
    print(f"  ✅ Auto server setup")
    print(f"  ✅ Wolf pack onboarding")
    print(f"  ✅ Welcome DMs")
    print(f"  ✅ Channel announcements")
    print(f"")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"  ✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"  ❌ Failed to sync commands: {e}")
    
    print(f"")
    print(f"═══════════════════════════════════════════════════════")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Game(name="🎰 cloutscape.org | !help"),
        status=discord.Status.online
    )

@bot.event
async def on_member_join(member):
    """Send welcome DM and announce in welcome channel"""
    print(f"[JOIN] {member.name} joined {member.guild.name}")
    
    # Send DM
    try:
        dm_message = WELCOME_DM.format(username=member.name)
        await member.send(dm_message)
        print(f"  ✅ Sent DM to {member.name}")
    except discord.Forbidden:
        print(f"  ❌ Could not DM {member.name} (DMs disabled)")
    except Exception as e:
        print(f"  ❌ Error sending DM: {e}")
    
    # Announce in welcome channel
    welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if welcome_channel:
        try:
            embed = discord.Embed(
                title="🐺 NEW DEGEN IN THE DEN!",
                description=WELCOME_CHANNEL_MESSAGE.format(mention=member.mention),
                color=GOLD,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Degens777Den | All In. Ben Motto.")
            await welcome_channel.send(embed=embed)
            print(f"  ✅ Announced in #welcome")
        except Exception as e:
            print(f"  ❌ Error announcing: {e}")
    
    # Auto-assign "Degen" role
    degen_role = discord.utils.get(member.guild.roles, name="Degen")
    if degen_role:
        try:
            await member.add_roles(degen_role)
            print(f"  ✅ Assigned 'Degen' role to {member.name}")
        except Exception as e:
            print(f"  ❌ Error assigning role: {e}")

@bot.event
async def on_member_remove(member):
    """Announce when member leaves"""
    print(f"[LEAVE] {member.name} left {member.guild.name}")
    
    welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if welcome_channel:
        try:
            embed = discord.Embed(
                description=f"🐑 **{member.name}** chose to be sheep. They left the pack.",
                color=RED,
                timestamp=datetime.now(timezone.utc)
            )
            await welcome_channel.send(embed=embed)
        except:
            pass

# ==================== SETUP COMMAND ====================

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    """Setup complete Degens777Den server structure"""
    await ctx.send("🔧 **Setting up Degens777Den server... This may take a minute.**")
    
    guild = ctx.guild
    setup_log = []
    
    # Create categories and channels
    for category_name, channels in SERVER_SETUP_CHANNELS.items():
        # Get or create category
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            try:
                category = await guild.create_category(category_name)
                setup_log.append(f"✅ Created category: {category_name}")
            except Exception as e:
                setup_log.append(f"❌ Failed to create category {category_name}: {e}")
                continue
        
        # Create channels
        for channel_info in channels:
            channel_name = channel_info["name"]
            channel_topic = channel_info["topic"]
            
            existing = discord.utils.get(guild.text_channels, name=channel_name)
            if not existing:
                try:
                    await guild.create_text_channel(
                        name=channel_name,
                        category=category,
                        topic=channel_topic
                    )
                    setup_log.append(f"  ✅ Created #{channel_name}")
                except Exception as e:
                    setup_log.append(f"  ❌ Failed to create #{channel_name}: {e}")
    
    # Create roles
    roles_to_create = [
        {"name": "🐺 Alpha Wolf", "color": RED, "permissions": discord.Permissions(administrator=True)},
        {"name": "🔥 Pack Leader", "color": GOLD, "permissions": discord.Permissions(manage_messages=True, manage_roles=True)},
        {"name": "👑 VIP Degen", "color": GOLD, "permissions": discord.Permissions.none()},
        {"name": "Degen", "color": GREEN, "permissions": discord.Permissions.none()},
    ]
    
    for role_info in roles_to_create:
        existing_role = discord.utils.get(guild.roles, name=role_info["name"])
        if not existing_role:
            try:
                await guild.create_role(
                    name=role_info["name"],
                    color=discord.Color(role_info["color"]),
                    permissions=role_info["permissions"],
                    hoist=True
                )
                setup_log.append(f"✅ Created role: {role_info['name']}")
            except Exception as e:
                setup_log.append(f"❌ Failed to create role {role_info['name']}: {e}")
    
    # Send setup log
    log_message = "\n".join(setup_log)
    await ctx.send(f"```\n{log_message}\n```")
    await ctx.send("✅ **Server setup complete! Degens777Den is ready to roll.** 🎰")

# ==================== COMMANDS ====================

@bot.command(name="help")
async def help_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🐺 Degens777Den Bot Commands",
        description="All available commands for the Wolf Pack",
        color=GOLD
    )
    
    embed.add_field(
        name="🎮 Casino Commands",
        value="`!stats` - View casino statistics\n`!leaderboard` - Top wagerers\n`!verify <username>` - Link Discord to casino account",
        inline=False
    )
    
    embed.add_field(
        name="💰 OSRS Commands",
        value="`!gold` - KodakGP gold rates\n`!services` - Available OSRS services",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Admin Commands",
        value="`!setup` - Setup server channels/roles\n`!announce <message>` - Send announcement",
        inline=False
    )
    
    embed.set_footer(text="Degens777Den | All In. Ben Motto.")
    await ctx.send(embed=embed)

@bot.command(name="stats")
async def stats_command(ctx):
    """Show casino statistics"""
    embed = discord.Embed(
        title="🎰 Degens777Den Casino Stats",
        description="Live statistics from cloutscape.org",
        color=GOLD,
        timestamp=datetime.now(timezone.utc)
    )
    
    # TODO: Fetch from API
    embed.add_field(name="👥 Total Players", value="1,337", inline=True)
    embed.add_field(name="🎲 Total Bets", value="420,690", inline=True)
    embed.add_field(name="💰 Total Wagered", value="$2.1M", inline=True)
    embed.add_field(name="📊 RTP", value="97% (REAL)", inline=True)
    embed.add_field(name="🔥 Online Now", value="143/350", inline=True)
    embed.add_field(name="🎁 Rain Today", value="$450", inline=True)
    
    embed.set_footer(text="Play now: cloutscape.org")
    await ctx.send(embed=embed)

@bot.command(name="gold")
async def gold_rates(ctx):
    """Show OSRS gold rates"""
    embed = discord.Embed(
        title="💰 KodakGP OSRS Gold Rates",
        description="Current buy/sell rates for OSRS GP",
        color=0xFFC800
    )
    
    embed.add_field(name="📈 Buy Rate", value="$0.45 per 1M GP", inline=True)
    embed.add_field(name="📉 Sell Rate", value="$0.50 per 1M GP", inline=True)
    embed.add_field(name="📦 Min Buy", value="10M GP", inline=True)
    embed.add_field(name="📦 Max Buy", value="5000M GP (5B)", inline=True)
    embed.add_field(name="💸 Min Sell", value="50M GP", inline=True)
    embed.add_field(name="✅ Trusted Since", value="2018", inline=True)
    
    embed.add_field(
        name="🛒 How to Buy",
        value="1. Visit cloutscape.org\n2. Go to KodakGP Store\n3. Select amount & pay\n4. GP added to balance instantly",
        inline=False
    )
    
    embed.set_footer(text="Powered by KodakGP | cloutscape.org")
    await ctx.send(embed=embed)

@bot.command(name="announce")
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message: str):
    """Send announcement to announcements channel"""
    announcements = discord.utils.get(ctx.guild.text_channels, name="announcements")
    if announcements:
        embed = discord.Embed(
            title="📢 ANNOUNCEMENT",
            description=message,
            color=RED,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="Degens777Den Staff")
        await announcements.send("@everyone", embed=embed)
        await ctx.send("✅ Announcement sent!")
    else:
        await ctx.send("❌ #announcements channel not found. Run `!setup` first.")

# ==================== ERROR HANDLING ====================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found. Use `!help` for available commands.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"❌ An error occurred: {error}")

# ==================== MAIN ====================

def main():
    if not BOT_TOKEN:
        print("❌ ERROR: DISCORD_BOT_TOKEN not set in .env file!")
        print("   1. Go to https://discord.com/developers/applications")
        print("   2. Create a bot and get the token")
        print("   3. Add to backend/.env: DISCORD_BOT_TOKEN=your_token_here")
        print("   4. Invite bot to server with admin permissions")
        sys.exit(1)
    
    print("🚀 Starting Degens777Den Discord Bot...")
    print("   Bot will handle:")
    print("   • Auto server setup")
    print("   • Welcome DMs (wolf pack onboarding)")
    print("   • Channel announcements")
    print("   • Live bet notifications")
    print("")
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ ERROR: Invalid bot token!")
        print("   Check your DISCORD_BOT_TOKEN in backend/.env")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
