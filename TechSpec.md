TXC bot — tech spec

Oct 3, 2026 · @Vaishnavi

Product overview

TXC bot is the custom Discord bot for the Tech X Creators server. It's one long-running Python process.


Feature	Status	Notes
Welcome message	Building (v1) --  spec below
Member counter -- Planned	
Mod logs	-- Planned	deletes, edits, joins/leaves, bans
Slash-command config	-- Planned	/welcome set-channel etc., SQLite

Feature 1: Welcome message

TXC bot posts a welcome msg in a set channel whenever a new member joins.

v1 scope

Welcome embed in a set channel on every join, pinging the new member

Pastel, cute styling: kaomoji, soft emojis, member pfp, member number
Optional welcome DM
Config through env vars (no slash commands yet)

Out of scope for v1: welcome card image, per-server config via slash commands.

Message design

The welcome is one embed with a short ping above it. The ping goes in the plain message content, since mentions inside an embed don't notify anyone.

Example output

markdown
Hey @Huemen, welcome to Tech X Creators! 🎀

[embed — pastel pink side bar, Huemen's pfp top-right]

So happy to have you here! ✨

Here's where you can build things,
share ideas, meet cool people & learn together. ♡

Before you start exploring:
୨୧ Read #rules
୨୧ Say hi in #introductions
୨୧ Find your people & start building 💻

Have fun & build something cool! 🫶

footer: you're member #152 ✨

Embed fields

Part	Value	Notes
Content (above embed)	Hey {mention}, welcome to **Tech X Creators**! 🎀	the only part that pings
Title	none	the greeting line already does this job
Description	intro, 3 ୨୧ steps, sign-off	"Before you start exploring:" in bold; channels as <#channel_id> so they're clickable
Color	
#FFB6C1 (pastel pink)	alternates: 
#C8A2FF lavender, 
#A7E8E0 mint
Thumbnail	member.display_avatar.url	server pfp, else global, else default
Image	none in v1	a cute banner gif can go here later
Footer	you're member #{count} ✨	from guild.member_count

Style rules: short lines, ୨୧ before each step, soft emojis only (🎀✨♡💻🫶), no walls of text. Plain-text fallback: put the whole message in content and drop the embed (loses the pfp and pink bar).

Behavior & flow

On each join the bot builds one embed and sends it once. A failed DM never blocks the channel message.

Discord fires on_member_join(member) (requires the Server Members intent).
Skip if member.bot is true and WELCOME_SKIP_BOTS=true.
Look up the welcome channel by WELCOME_CHANNEL_ID. If it's missing, log a warning and stop.
Build the embed from the template (section above).
Send it with the ping as content and allowed_mentions limited to that one user.
If WELCOME_DM=true, DM a short cute note. Catch discord.Forbidden (DMs closed) and move on.

Discord's built-in join message: the grey "Huemen is here. Wave to say hi!" line comes from Discord itself, not a bot. Turn it off in Server Settings → System Messages ("send a random welcome message when someone joins"), otherwise every join shows two welcomes. Also remove the YAGPDB welcome once TXC bot is live.

Tech stack & setup

Python 3.11+ with discord.py 2.x and python-dotenv. There's no database or web server in v1, just one long-running process.

Developer portal

Bot username TXC bot, custom pfp (square PNG, 512×512)
Privileged intent: Server Members Intent on (Message Content isn't needed)
Invite scope bot; permissions View Channels, Send Messages, Embed Links

Config (.env)

Key	Example	Purpose
DISCORD_TOKEN	MTIz…	bot token, never committed
WELCOME_CHANNEL_ID	1234567890	where welcomes go
RULES_CHANNEL_ID	1234567891	linked in step 1
INTRO_CHANNEL_ID	1234567892	linked in step 2
WELCOME_COLOR	FFB6C1	embed hex color
WELCOME_DM	true	send the DM or not
WELCOME_SKIP_BOTS	true	ignore bots joining

.env goes in .gitignore from the first commit.

Implementation plan

The bot uses commands.Bot with one cog from day one, so logs and a counter can be added later as separate cogs.

File structure

markdown
txc-bot/
├── bot.py            # entrypoint: intents, load cogs, run
├── config.py         # reads + validates .env
├── cogs/
│   └── welcome.py    # on_member_join listener
├── utils/
│   └── embeds.py     # build_welcome_embed(member, cfg)
├── requirements.txt
├── Dockerfile
├── .env.example
└── .gitignore

Key functions

Function	File	Does
load_config()	config.py	reads env, casts IDs to int, fails fast if a key is missing
build_welcome_embed(member, cfg)	utils/embeds.py	returns the styled discord.Embed
ordinal(n)	utils/embeds.py	1 → 1st, 152 → 152nd, 113 → 113th
Welcome.on_member_join(member)	cogs/welcome.py	runs the flow above

Edge cases

Welcome channel deleted or ID wrong: log a warning, don't crash.
Bot missing Send Messages or Embed Links in that channel: catch discord.Forbidden and log it.
Member DMs closed: skip the DM silently.
Mass joins (raids): sends are rate-limited by Discord; discord.py queues them, which is acceptable for v1.
Member leaves before the send: the message still posts, which is fine.
member_count can be briefly stale: cosmetic only.
Testing, deployment & future scope

Testing

 Make a private test server and point WELCOME_CHANNEL_ID at it
 Join with an alt account and check the ping, pfp, ordinal and clickable channels
 Test with DMs closed on the alt: the channel message still sends
 Use a wrong channel ID: the bot logs a warning and doesn't crash
 Remove Embed Links from the bot's role: the error is logged
 Check the embed in both dark and light mode
 Unit-test ordinal() (1, 2, 3, 11, 12, 13, 21, 111, 152)

Deployment

Package it as a Docker image (python:3.11-slim) and run it on any always-on host, with the token passed as an env var. Options: Oracle Cloud's always-free VM, a free bot host (watch for manual renewals), or a home machine. Use restart: unless-stopped so it recovers from crashes.

Future scope (as separate cogs)

Welcome card image with Pillow (pfp + name on a pastel banner)
Auto-role on join
Goodbye message on on_member_remove
Member counter voice channel (renames are rate-limited to about 2 per 10 min)
Mod logs: deletes, edits, joins/leaves, bans
Slash commands like /welcome set-channel and /welcome preview, with config in SQLite