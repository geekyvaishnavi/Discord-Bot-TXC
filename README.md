# TXC Bot

A Discord bot for the **Tech X Creators** community server, written in Python with [discord.py](https://github.com/Rapptz/discord.py).

## Features

- **Welcome message** — when someone joins, the bot pings them in a welcome channel with links to the rules and introductions channels.
- **Optional welcome DM** — a short welcome sent privately to new members (off by default).
- **Mod logs** — deleted and edited messages, joins/leaves, bans and unbans are posted to a private mod-log channel (optional).

Planned: member counter and slash-command configuration. See [TechSpec.md](TechSpec.md).

## Setup

### 1. Create a Discord application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a **New Application**.
2. Under **Bot**, click **Reset Token** and copy the token.
3. Under **Bot → Privileged Gateway Intents**, turn on **Server Members Intent** (required to detect joins) and **Message Content Intent** (required to log deleted/edited message text).
4. Under **OAuth2 → URL Generator**, select the `bot` scope and the **View Channels**, **Send Messages**, **Embed Links**, **Read Message History**, and **View Audit Log** permissions. Open the generated URL to invite the bot to your server.

### 2. Install

Requires Python 3.13+.

```bash
git clone https://github.com/geekyvaishnavi/Discord-Bot-TXC.git
cd Discord-Bot-TXC
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Fill in `.env`:

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Your bot token |
| `WELCOME_CHANNEL_ID` | Channel where welcome messages are posted |
| `RULES_CHANNEL_ID` | Rules channel linked in the welcome message |
| `INTRO_CHANNEL_ID` | Introductions channel linked in the welcome message |
| `WELCOME_DM_ENABLED` | `true` to also DM new members, `false` otherwise |
| `MOD_LOG_CHANNEL_ID` | Private channel for mod logs; leave empty to disable |

To copy channel IDs, enable **Developer Mode** in Discord (User Settings → Advanced), then right-click a channel → **Copy Channel ID**.

### 4. Run

```bash
python bot.py
```

On startup the bot prints whether it can see the welcome channel and has permission to post there.

## Troubleshooting

- **No welcome message when someone joins** — make sure **Server Members Intent** is enabled and the bot has been invited to the server.
- **"Welcome channel … not visible to the bot"** — check the channel ID, and that the bot's role can view and send messages in that channel.
- **Deleted messages show "content is unknown"** — the bot only remembers messages sent while it's running. Messages from before the last restart can't be recovered.
- **Ban logs don't say who banned** — give the bot the **View Audit Log** permission.
