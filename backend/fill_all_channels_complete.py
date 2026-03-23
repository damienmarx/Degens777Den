#!/usr/bin/env python3
"""
COMPLETE Discord Channel Filler
Fills ALL channels with content, game guides, and images
"""

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

GOLD = 0xD4AF37
RED = 0xDC143C
GREEN = 0x00FF87
CYAN = 0x00E0FF

# Image URLs
IMG_WOLVES_VS_SHEEP = ""
IMG_LAUNCH_BONUS = ""
IMG_CASINO_LUXURY = ""
IMG_KODAKGP_GOLD = ""
IMG_PATTERN = ""

# Channel content - COMPLETE
CHANNEL_CONTENT = {
    "welcome": [
        {
            "title": "🐺 WELCOME TO DEGENS777DEN - THE WOLF PACK",
            "description": """
**You've entered the DEN where REAL degens hunt together.**

**THE CHOICE IS YOURS:**
🐺 **EAT WITH THE WOLVES** - Transparent 97% RTP
🐑 **BE SLAUGHTERED WITH THE SHEEP** - RuneHall/RuneChat scams

═══════════════════════════════════════

**🎰 6 PROVABLY FAIR GAMES:**
🎲 Dice • 🎰 Keno • 🚀 Crash • 🎡 Wheel • 📍 Plinko • 🎯 Limbo

**💰 WELCOME BONUS:** $5 USD or 35M OSRS GP
**👑 VIP REWARDS:** Up to 15% rakeback + 10% lossback
**🎁 FIRST 100 MEMBERS:** Double bonus!

**🔗 PLAY NOW:** https://cloutscape.org

*"All In. Ben Motto."* 🎲
            """,
            "color": GOLD,
            "image": IMG_WOLVES_VS_SHEEP
        }
    ],
    
    "announcements": [
        {
            "title": "🚀 DEGENS777DEN LAUNCHING SOON!",
            "description": "**Pre-Launch Phase Active**\n\nFirst 100 members get DOUBLE welcome bonus!\n10,000M OSRS GP tournament on launch day!\n\nhttps://cloutscape.org",
            "color": RED,
            "image": IMG_LAUNCH_BONUS
        }
    ],
    
    "general-chat": [
        {
            "title": "🎲 DICE GAME GUIDE",
            "description": """
**Classic provably fair dice**

**How to Play:**
• Roll UNDER or OVER a number (1-99)
• Choose your multiplier (1.01× to 9900×)
• Higher risk = Higher reward

**Popular Strategies:**
• 50% chance = 1.98× payout (balanced)
• 10% chance = 9.70× payout (risky)
• 1% chance = 97× payout (extreme)

**Provably Fair:** Every roll verifiable with SHA-256

**Play Now:** https://cloutscape.org
            """,
            "color": GOLD,
            "image": IMG_CASINO_LUXURY
        },
        {
            "title": "🎰 KENO GAME GUIDE",
            "description": """
**RuneScape-style Keno**

**How to Play:**
• Pick 1-10 numbers from 40
• 10 balls drawn
• More matches = Higher payout

**Max Payout:** 10,000× (all 10 numbers)

**Strategy:** 5-7 numbers for best balance

**Play Now:** https://cloutscape.org
            """,
            "color": CYAN
        },
        {
            "title": "🚀 CRASH GAME GUIDE",
            "description": """
**Ride the rocket, cash out before crash**

**How to Play:**
• Place bet before round starts
• Multiplier increases (1.00×, 1.50×, 2.00×...)
• Cash out before crash
• Crash point is provably fair

**Strategies:**
• Conservative: Auto cash @ 2×
• Balanced: Cash @ 3-5×
• Risky: Hold for 10×+

**Play Now:** https://cloutscape.org
            """,
            "color": GREEN
        }
    ],
    
    "gold-trades": [
        {
            "title": "💰 KODAKGP - OSRS GOLD PROVIDER",
            "description": """
**Trusted gold provider since 2018**

**BUY GOLD:**
• $0.45 per 1M GP
• Min: 10M | Max: 5B
• Instant delivery to casino balance

**SELL GOLD:**
• $0.50 per 1M GP
• Min: 50M
• Payment in crypto/PayPal < 24hrs

**SERVICES:**
• Pure accounts (all combat levels)
• Quest services (RFD, MM2, DS2)
• Fire Cape / Infernal Cape
• Diary completion

**Contact:** @KodakGP
            """,
            "color": 0xFFC800,
            "image": IMG_KODAKGP_GOLD
        }
    ],
    
    "big-wins": [
        {
            "title": "🏆 HALL OF FAME",
            "description": """
**Post your BIG WINS here!**

Tag @everyone for wins over 100×

**Legendary Wins:**
💎 1000× on Crash = 1B GP
🎲 500× on Plinko = 500M GP
🚀 97× on Dice = 970M GP

**Your turn!** 🐺
            """,
            "color": GREEN,
            "image": IMG_PATTERN
        }
    ],
    
    "why-degens": [
        {
            "title": "🚨 RUNEHALL & RUNECHAT EXPOSED",
            "description": """
**WHY THEY'RE SCAMS:**

**1. JWT Token Injection**
- Fake balance displays
- Lock withdrawals

**2. Dynamic RTP**
- Claims 96%, reality 88-92%
- Changes after deposits

**3. Fake Provably Fair**
- Pre-selected seeds
- Can't verify after cashout

**4. Withdrawal Traps**
- 3-7 day "processing"
- Hope you gamble it back

**DEGENS777DEN DIFFERENCE:**
✅ Real 97% RTP
✅ True provably fair
✅ Instant withdrawals
✅ No manipulation

**STOP BEING SHEEP. JOIN THE WOLVES.**
            """,
            "color": RED
        }
    ]
}

@bot.event
async def on_ready():
    print(f"✅ Channel Filler Bot Ready")
    guild = bot.get_guild(GUILD_ID)
    
    if not guild:
        print(f"❌ Guild not found!")
        await bot.close()
        return
    
    print(f"📝 Filling ALL channels with content...")
    
    for channel_name, embeds_data in CHANNEL_CONTENT.items():
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            try:
                for embed_data in embeds_data:
                    embed = discord.Embed(
                        title=embed_data["title"],
                        description=embed_data["description"],
                        color=embed_data["color"]
                    )
                    if "image" in embed_data:
                        embed.set_image(url=embed_data["image"])
                    
                    await channel.send(embed=embed)
                    await asyncio.sleep(2)
                
                print(f"  ✅ Posted to #{channel_name}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print(f"  ⚠️  #{channel_name} not found")
    
    print(f"\n🎉 ALL CHANNELS FILLED!")
    await bot.close()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
