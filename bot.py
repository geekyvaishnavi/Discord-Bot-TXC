import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_TOKEN"]
WELCOME_CHANNEL_ID = int(os.environ["WELCOME_CHANNEL_ID"])
RULES_CHANNEL_ID = int(os.environ["RULES_CHANNEL_ID"])
INTRO_CHANNEL_ID = int(os.environ["INTRO_CHANNEL_ID"])
WELCOME_DM_ENABLED = os.getenv("WELCOME_DM_ENABLED", "false").lower() == "true"

intents = discord.Intents.default()
intents.members = True  # privileged; required for on_member_join
client = discord.Client(intents=intents)


def build_welcome_content(member: discord.Member) -> str:
    return (
        f"Hey {member.mention}, welcome to **Tech X Creators**! 👋\n\n"
        "We’re glad to have you here. \n\n"
        "A space for **developers, creators, builders, and curious minds** "
        "to connect, learn, and create together.\n\n"
        "**Start here:**\n"
        f"✦ Read the <#{RULES_CHANNEL_ID}>\n"
        f"✦ Introduce yourself in <#{INTRO_CHANNEL_ID}>\n"
        "✦ Meet the community and start building. 💻\n\n"
        "**We’re excited to have you with us. 🩷**"
    )


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (◕‿◕)")
    print(f"Members intent enabled: {client.intents.members}")
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        print(f"⚠ Welcome channel {WELCOME_CHANNEL_ID} not visible to the bot — check the ID / bot's access")
        return
    perms = channel.permissions_for(channel.guild.me)
    print(
        f"Welcome channel: #{channel.name} in {channel.guild.name} | "
        f"view={perms.view_channel} send={perms.send_messages}"
    )


@client.event
async def on_member_join(member: discord.Member):
    print(f"Member joined: {member} in {member.guild.name}")
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        print(f"Welcome channel {WELCOME_CHANNEL_ID} not found in {member.guild.name}")
        return

    await channel.send(
        content=build_welcome_content(member),
        allowed_mentions=discord.AllowedMentions(users=True, everyone=False, roles=False),
    )

    if WELCOME_DM_ENABLED:
        try:
            await member.send(
                f"Welcome to **Tech X Creators**, {member.name}! ♡ (づ｡◕‿‿◕｡)づ\n"
                f"Start by reading <#{RULES_CHANNEL_ID}> and saying hi in <#{INTRO_CHANNEL_ID}>."
            )
        except discord.Forbidden:
            pass  # member has DMs closed


client.run(TOKEN)
