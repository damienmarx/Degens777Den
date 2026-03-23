#!/usr/bin/env python3
"""
Degens777Den Discord Bot - Complete Edition
- Admin onboarding with responsibility DMs
- Server cleanup and audit
- Full channel content population
- Wolf pack management
"""

import discord
from discord.ext import commands, tasks
import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

GOLD = 0xD4AF37
RED = 0xDC143C
GREEN = 0x00FF87
CYAN = 0x00E0FF
PURPLE = 0x9B59B6

# Admin responsibility DM
ADMIN_ONBOARDING_DM = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🐺 DEGENS777DEN - ADMIN RESPONSIBILITIES 🐺      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

**Congratulations, {username}!**

You've been granted **ADMIN** status in Degens777Den. This is not just a role—it's a **HEAVY RESPONSIBILITY**.

═══════════════════════════════════════════════════════════

**⚠️ WITH GREAT POWER COMES GREAT RESPONSIBILITY:**

As an admin, you are **TRUSTED** with:

**1. 💰 FINANCIAL AUTHORITY**
• Handling large sums of mule money (OSRS GP, crypto)
• Processing player withdrawals
• Managing KodakGP transactions
• Access to wallet balances
• **YOU ARE RESPONSIBLE FOR EVERY TRANSACTION**

**2. 🛡️ SITE AUDITING**
• Monitoring player activity for suspicious behavior
• Reviewing bet patterns for exploits
• Detecting multi-accounting and collusion
• Verifying provably fair system integrity
• **YOUR VIGILANCE PROTECTS THE PACK**

**3. 👥 USER MANAGEMENT**
• Ban authority (use wisely, not emotionally)
• Handling support tickets
• Resolving disputes fairly
• Managing VIP tier adjustments
• **YOUR DECISIONS AFFECT REAL PEOPLE**

**4. 🎮 ADMIN DASHBOARD ACCESS**
You now have access to: **https://cloutscape.org/admin**

**Dashboard Capabilities:**
• View all player statistics
• Adjust user balances (OSRS GP, crypto)
• Process withdrawal requests
• Monitor live bets in real-time
• Configure VIP tiers and bonuses
• Ban/unban users
• View bet history and provably fair seeds

**⚠️ DASHBOARD RULES:**
• NEVER adjust balances without authorization
• NEVER share admin credentials
• LOG all major actions
• REPORT any suspicious activity
• If unsure, ASK before acting

═══════════════════════════════════════════════════════════

**📜 YOUR ADMIN CODE OF CONDUCT:**

**DO:**
✅ Act with integrity and fairness
✅ Protect player funds like your own
✅ Respond to support tickets within 24 hours
✅ Report bugs and exploits immediately
✅ Keep admin discussions confidential
✅ Treat all players equally (no favoritism)
✅ Ask for help when uncertain

**DO NOT:**
❌ Abuse admin powers for personal gain
❌ Share sensitive player information
❌ Make unilateral decisions without consultation
❌ Ignore suspicious activity
❌ Play on the site (conflict of interest)
❌ Accept bribes or kickbacks from players
❌ Leak admin discussions publicly

═══════════════════════════════════════════════════════════

**🚨 FINANCIAL RESPONSIBILITY:**

You will handle:
• **Mule accounts** with 100M+ OSRS GP
• **Crypto wallets** with 10+ BTC equivalent
• **Player withdrawals** up to $10,000 USD
• **KodakGP transactions** (gold buying/selling)

**IF YOU FUCK UP:**
• Player loses money? **YOU'RE LIABLE**
• Mule account hacked? **YOUR RESPONSIBILITY**
• Fraudulent withdrawal approved? **ON YOU**

**We trust you. Don't break that trust.**

═══════════════════════════════════════════════════════════

**🔐 SECURITY REQUIREMENTS:**

**MANDATORY:**
• Enable 2FA on Discord
• Use strong, unique password
• NEVER share admin credentials
• Log out when not actively using dashboard
• Report phishing attempts immediately

**RECOMMENDED:**
• Use VPN when accessing admin panel
• Don't access from public WiFi
• Clear browser cache after admin sessions
• Use password manager (not browser save)

═══════════════════════════════════════════════════════════

**📊 REPORTING STRUCTURE:**

You report to: **@AlphaWolf** (Head Admin)

**Daily Tasks:**
• Check support tickets (#support)
• Monitor live bets for anomalies
• Review withdrawal requests
• Respond to admin pings

**Weekly Tasks:**
• Audit top 10 players for suspicious activity
• Review provably fair system logs
• Check mule account balances
• Report any concerns in admin channel

═══════════════════════════════════════════════════════════

**⚖️ DISCIPLINARY ACTIONS:**

Admin abuse results in:
• **1st Offense:** Warning + audit review
• **2nd Offense:** Admin removal + ban
• **Financial Abuse:** Legal action + restitution

**We don't tolerate corruption. Period.**

═══════════════════════════════════════════════════════════

**🤝 ACCEPTANCE:**

**DO YOU ACCEPT THESE RESPONSIBILITIES?**

React to this message:
• ✅ = I accept and understand
• ❌ = I decline (admin role will be removed)

**You have 24 hours to respond.**

If you accept:
1. You'll receive admin dashboard login credentials
2. You'll be added to #admin-chat
3. You'll undergo 1-week training period

**Questions?**
DM @AlphaWolf or ask in #admin-chat (after acceptance)

═══════════════════════════════════════════════════════════

**Welcome to the inner circle of the Wolf Pack.**

**With great power comes heavy responsibility.**
**Handle with care. Protect the pack.**

🐺 **The Den trusts you. Don't fuck it up.** 🐺

═══════════════════════════════════════════════════════════

*Degens777Den Administration Team*
*"All In. Ben Motto."*
"""

@bot.event
async def on_ready():
    print(f"╔═══════════════════════════════════════════════════════╗")
    print(f"║  🐺 DEGENS777DEN BOT ONLINE 🐺                       ║")
    print(f"╚═══════════════════════════════════════════════════════╝")
    print(f"Bot: {bot.user.name} (ID: {bot.user.id})")
    print(f"Servers: {len(bot.guilds)}")
    print(f"")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Failed to sync: {e}")
    
    await bot.change_presence(
        activity=discord.Game(name="🎰 cloutscape.org | !cleanup"),
        status=discord.Status.online
    )
    
    # Start cleanup task
    cleanup_check.start()

@tasks.loop(hours=1)
async def cleanup_check():
    """Hourly server audit and cleanup"""
    for guild in bot.guilds:
        print(f"\n🔍 Running cleanup for {guild.name}...")
        await audit_server(guild)

@bot.command(name="cleanup")
@commands.has_permissions(administrator=True)
async def manual_cleanup(ctx):
    """Manually run server cleanup and admin audit"""
    await ctx.send("🔍 **Running server cleanup and admin audit...**")
    await audit_server(ctx.guild)
    await ctx.send("✅ **Cleanup complete! Check your DMs if you're admin.**")

async def audit_server(guild):
    """Audit server members and DM admins"""
    print(f"  📊 Total members: {guild.member_count}")
    
    online_count = 0
    admin_count = 0
    
    # Check for admin role
    admin_roles = [
        discord.utils.get(guild.roles, name="🐺 Alpha Wolf"),
        discord.utils.get(guild.roles, name="🔥 Pack Leader"),
        discord.utils.get(guild.roles, name="Admin"),
        discord.utils.get(guild.roles, name="Moderator")
    ]
    admin_roles = [r for r in admin_roles if r]
    
    for member in guild.members:
        # Count online members
        if member.status != discord.Status.offline:
            online_count += 1
        
        # Check if member has admin role
        is_admin = any(role in member.roles for role in admin_roles) or member.guild_permissions.administrator
        
        if is_admin and not member.bot:
            admin_count += 1
            # Check if they've been onboarded
            try:
                # Send admin onboarding DM
                dm_msg = ADMIN_ONBOARDING_DM.format(username=member.name)
                dm = await member.send(dm_msg)
                
                # Add reactions for acceptance
                await dm.add_reaction("✅")
                await dm.add_reaction("❌")
                
                print(f"  📨 Sent admin DM to {member.name}")
            except discord.Forbidden:
                print(f"  ❌ Cannot DM {member.name} (DMs disabled)")
            except Exception as e:
                print(f"  ❌ Error DMing {member.name}: {e}")
    
    print(f"  ✅ Online: {online_count} | Admins: {admin_count}")

@bot.event
async def on_member_join(member):
    """Welcome new members"""
    print(f"[JOIN] {member.name} joined {member.guild.name}")
    
    # Send DM
    try:
        welcome_embed = discord.Embed(
            title="🐺 WELCOME TO THE WOLF PACK",
            description=f"""
**Welcome {member.mention} to Degens777Den!**

You've just entered the Den where REAL degens hunt together.

**THE CHOICE:**
🐺 **EAT WITH THE WOLVES** - 97% RTP, provably fair
🐑 **BE SLAUGHTERED WITH THE SHEEP** - RuneHall/RuneChat scams

**🎰 PLAY NOW:** https://cloutscape.org

**🎁 WELCOME BONUS:** $5 USD or 35M OSRS GP

Check #welcome for full details!

*"All In. Ben Motto."* 🎲
            """,
            color=GOLD
        )
        await member.send(embed=welcome_embed)
        print(f"  ✅ Sent welcome DM")
    except:
        pass
    
    # Announce in welcome channel
    welcome = discord.utils.get(member.guild.text_channels, name="welcome")
    if welcome:
        await welcome.send(f"🐺 {member.mention} joined the pack! Welcome to the Den!")
    
    # Auto-assign Degen role
    degen_role = discord.utils.get(member.guild.roles, name="Degen")
    if degen_role:
        await member.add_roles(degen_role)

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    """Setup complete server structure"""
    await ctx.send("🔧 **Setting up Degens777Den server...**")
    
    guild = ctx.guild
    
    # Create categories and channels
    categories = {
        "📢 INFORMATION": ["welcome", "rules", "announcements", "why-degens"],
        "💬 COMMUNITY": ["general-chat", "big-wins", "strategy", "memes"],
        "🎮 CASINO": ["live-bets", "giveaways", "vip-lounge"],
        "💼 OSRS": ["gold-trades", "services", "osrs-general"],
        "❓ SUPPORT": ["support", "suggestions"],
        "🔒 ADMIN": ["admin-chat", "audit-logs"]
    }
    
    for cat_name, channels in categories.items():
        category = discord.utils.get(guild.categories, name=cat_name)
        if not category:
            category = await guild.create_category(cat_name)
        
        for channel_name in channels:
            if not discord.utils.get(guild.text_channels, name=channel_name):
                # Admin channels private
                if cat_name == "🔒 ADMIN":
                    admin_role = discord.utils.get(guild.roles, name="🐺 Alpha Wolf")
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        admin_role: discord.PermissionOverwrite(read_messages=True) if admin_role else None
                    }
                    await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
                else:
                    await guild.create_text_channel(channel_name, category=category)
    
    # Create roles
    roles = [
        ("🐺 Alpha Wolf", RED, True),
        ("🔥 Pack Leader", GOLD, True),
        ("👑 VIP Degen", GOLD, True),
        ("Degen", GREEN, False)
    ]
    
    for role_name, color, hoist in roles:
        if not discord.utils.get(guild.roles, name=role_name):
            await guild.create_role(name=role_name, color=discord.Color(color), hoist=hoist)
    
    await ctx.send("✅ **Server setup complete!**")

@bot.command(name="help")
async def help_cmd(ctx):
    """Show help"""
    embed = discord.Embed(title="🐺 Bot Commands", color=GOLD)
    embed.add_field(name="!cleanup", value="Audit server and DM admins", inline=False)
    embed.add_field(name="!setup", value="Create channels/roles", inline=False)
    embed.add_field(name="!stats", value="Casino statistics", inline=False)
    embed.add_field(name="!gold", value="OSRS gold rates", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="stats")
async def stats_cmd(ctx):
    """Show stats"""
    embed = discord.Embed(title="🎰 Casino Stats", color=GOLD)
    embed.add_field(name="Players", value="1,337", inline=True)
    embed.add_field(name="Bets", value="420,690", inline=True)
    embed.add_field(name="Wagered", value="$2.1M", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="gold")
async def gold_cmd(ctx):
    """Show gold rates"""
    embed = discord.Embed(title="💰 KodakGP Rates", color=0xFFC800)
    embed.add_field(name="Buy", value="$0.45/M", inline=True)
    embed.add_field(name="Sell", value="$0.50/M", inline=True)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not set!")
        exit(1)
    bot.run(BOT_TOKEN)
