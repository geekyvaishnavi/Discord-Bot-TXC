import logging
import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_TOKEN"]
WELCOME_CHANNEL_ID = int(os.environ["WELCOME_CHANNEL_ID"])
RULES_CHANNEL_ID = int(os.environ["RULES_CHANNEL_ID"])
INTRO_CHANNEL_ID = int(os.environ["INTRO_CHANNEL_ID"])
WELCOME_DM_ENABLED = os.getenv("WELCOME_DM_ENABLED", "false").lower() == "true"
# Optional: mod logs are disabled when unset
MOD_LOG_CHANNEL_ID = int(os.getenv("MOD_LOG_CHANNEL_ID") or 0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("txc_bot")

intents = discord.Intents.default()
intents.members = True  # privileged; required for on_member_join
intents.message_content = True  # privileged; required to log deleted/edited message text
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
    log.info(f"Logged in as {client.user} (ID: {client.user.id})")
    log.info(f"Members intent enabled: {client.intents.members}")
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        log.warning(f"Welcome channel {WELCOME_CHANNEL_ID} not visible to the bot — check the ID / bot's access")
        return
    perms = channel.permissions_for(channel.guild.me)
    log.info(
        f"Welcome channel: #{channel.name} in {channel.guild.name} | "
        f"view={perms.view_channel} send={perms.send_messages}"
    )

    if not MOD_LOG_CHANNEL_ID:
        log.info("Mod logs disabled (MOD_LOG_CHANNEL_ID not set)")
        return
    mod_channel = client.get_channel(MOD_LOG_CHANNEL_ID)
    if mod_channel is None:
        log.warning(f"Mod log channel {MOD_LOG_CHANNEL_ID} not visible to the bot — check the ID / bot's access")
        return
    perms = mod_channel.permissions_for(mod_channel.guild.me)
    log.info(
        f"Mod log channel: #{mod_channel.name} | send={perms.send_messages} "
        f"embed={perms.embed_links} audit_log={mod_channel.guild.me.guild_permissions.view_audit_log}"
    )


@client.event
async def on_member_join(member: discord.Member):
    log.info(f"Member joined: {member} in {member.guild.name}")
    embed = discord.Embed(
        title="Member joined",
        description=f"{member.mention} ({member})",
        color=discord.Color.green(),
    )
    embed.add_field(name="Account created", value=discord.utils.format_dt(member.created_at, "R"))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"User ID: {member.id}")
    await send_mod_log(member.guild, embed)

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        log.warning(f"Welcome channel {WELCOME_CHANNEL_ID} not found in {member.guild.name}")
        return

    await channel.send(
        content=build_welcome_content(member),
        allowed_mentions=discord.AllowedMentions(users=True, everyone=False, roles=False),
    )

    if WELCOME_DM_ENABLED:
        try:
            await member.send(
                f"Welcome to **Tech X Creators**, {member.name}!\n"
                f"Start by reading <#{RULES_CHANNEL_ID}> and saying hi in <#{INTRO_CHANNEL_ID}>."
            )
        except discord.Forbidden:
            log.info(f"Could not DM {member} (DMs closed)")


# --- Mod logs ---

def truncate(text: str, limit: int = 1024) -> str:
    # Embed field values are capped at 1024 characters
    if not text:
        return "*(no text)*"
    return text if len(text) <= limit else text[: limit - 1] + "…"


async def send_mod_log(guild: discord.Guild, embed: discord.Embed):
    if not MOD_LOG_CHANNEL_ID:
        return
    channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
    if channel is None:
        log.warning(f"Mod log channel {MOD_LOG_CHANNEL_ID} not found in {guild.name}")
        return
    embed.timestamp = discord.utils.utcnow()
    try:
        await channel.send(embed=embed)
    except discord.Forbidden:
        log.warning(f"No permission to post in mod log channel #{channel.name}")


async def find_audit_entry(guild: discord.Guild, action: discord.AuditLogAction, target_id: int):
    # Who did it and why; needs the View Audit Log permission
    try:
        async for entry in guild.audit_logs(limit=5, action=action):
            if entry.target and entry.target.id == target_id:
                return entry
    except discord.Forbidden:
        log.warning(f"Can't read audit log in {guild.name} — give the bot the View Audit Log permission")
    return None


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    if payload.guild_id is None or payload.channel_id == MOD_LOG_CHANNEL_ID:
        return
    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    # Raw event so deletes are logged even when the message isn't in the bot's cache
    message = payload.cached_message
    if message is not None and message.author.bot:
        return

    embed = discord.Embed(title="Message deleted", color=discord.Color.red())
    embed.add_field(name="Channel", value=f"<#{payload.channel_id}>")
    if message is not None:
        embed.add_field(name="Author", value=f"{message.author.mention} ({message.author})")
        embed.add_field(name="Content", value=truncate(message.content), inline=False)
        if message.attachments:
            names = "\n".join(a.filename for a in message.attachments)
            embed.add_field(name="Attachments", value=truncate(names), inline=False)
    else:
        embed.description = "Message was sent before the bot started, so its content is unknown."
    embed.set_footer(text=f"Message ID: {payload.message_id}")
    await send_mod_log(guild, embed)


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    # Also fires for embed/link-preview updates; only log real text changes
    if after.guild is None or after.author.bot or before.content == after.content:
        return

    embed = discord.Embed(
        title="Message edited",
        description=f"[Jump to message]({after.jump_url})",
        color=discord.Color.orange(),
    )
    embed.add_field(name="Channel", value=after.channel.mention)
    embed.add_field(name="Author", value=f"{after.author.mention} ({after.author})")
    embed.add_field(name="Before", value=truncate(before.content), inline=False)
    embed.add_field(name="After", value=truncate(after.content), inline=False)
    embed.set_footer(text=f"Message ID: {after.id}")
    await send_mod_log(after.guild, embed)


@client.event
async def on_member_remove(member: discord.Member):
    embed = discord.Embed(
        title="Member left",
        description=f"{member.mention} ({member})",
        color=discord.Color.dark_grey(),
    )
    if member.joined_at:
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, "R"))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"User ID: {member.id}")
    await send_mod_log(member.guild, embed)


@client.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    embed = discord.Embed(
        title="Member banned",
        description=f"{user.mention} ({user})",
        color=discord.Color.dark_red(),
    )
    entry = await find_audit_entry(guild, discord.AuditLogAction.ban, user.id)
    if entry is not None:
        embed.add_field(name="Banned by", value=entry.user.mention)
        embed.add_field(name="Reason", value=truncate(entry.reason or "No reason given"), inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"User ID: {user.id}")
    await send_mod_log(guild, embed)


@client.event
async def on_member_unban(guild: discord.Guild, user: discord.User):
    embed = discord.Embed(
        title="Member unbanned",
        description=f"{user.mention} ({user})",
        color=discord.Color.blue(),
    )
    entry = await find_audit_entry(guild, discord.AuditLogAction.unban, user.id)
    if entry is not None:
        embed.add_field(name="Unbanned by", value=entry.user.mention)
    embed.set_footer(text=f"User ID: {user.id}")
    await send_mod_log(guild, embed)


# log_handler=None: use the logging setup above instead of discord.py's own
client.run(TOKEN, log_handler=None)
