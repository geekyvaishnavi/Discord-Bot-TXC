# TXC Bot — Technical Specification

**Date:** October 3, 2026  
**Author:** @Vaishnavi  
**Status:** Draft

---

## 1. Product Overview

TXC Bot is a custom Discord bot for the **Tech X Creators** server. It runs as one long-running Python process.

### Feature Status

| Feature | Status | Notes |
|---|---|---|
| Welcome message | Building (V1) | See detailed specification below |
| Member counter | Planned | Member Count |
| Mod logs | Building (V1) | See detailed specification below |
| Slash-command config | Planned | `/welcome set-channel`, etc., with SQLite |

---

# 2. Feature 1: Welcome Message

TXC Bot posts a welcome message in a configured channel whenever a new member joins the server.

## 2.1 V1 Scope

The welcome system will include:

- Welcome embed in a configured channel on every join
- Ping the new member
- Pastel/cute styling
- Kaomoji and soft emojis
- Member profile picture
- Member number
- Optional welcome DM
- Configuration through environment variables

### Out of Scope for V1

- Welcome card image
- Per-server configuration through slash commands

---

# 3. Message Design

The welcome consists of a **plain-text ping above a single embed**.

The ping must be sent through the message `content` because mentions inside an embed do not notify the user.

## 3.1 Example Output

### Message Content

```text
Hey {mention}, welcome to **Tech X Creators**! 

We’re happy to have you here. 

You’ve just joined a community of **developers, creators, builders, and curious minds** — a space to learn, share ideas, collaborate, and build together.

**A few places to get started:**

› Read the <#RULES_CHANNEL_ID>  
› Introduce yourself in <#INTRO_CHANNEL_ID>  
› Meet the community, share your work, and start building. 💻

Bring your ideas, ask questions, share what you’re working on, and don’t be afraid to experiment.

**Glad to have you with us. Welcome to TXC! 🩷**

---

# 4. Feature 2: Mod Logs

TXC Bot posts an embed to a private mod-log channel whenever a moderation-relevant event happens, so moderators can review activity after the fact.

## 4.1 V1 Scope

The mod log system will include:

- Deleted messages: channel, author, content and attachment names
- Edited messages: channel, author, before/after content and a jump link
- Member joins: account age and avatar
- Member leaves: when they originally joined
- Bans and unbans: who did it and the reason, read from the audit log
- One colour per event type (deleted red, edited orange, joined green, left grey, banned dark red, unbanned blue)
- User or message ID in the footer and a timestamp on every entry
- Configuration through the `MOD_LOG_CHANNEL_ID` environment variable; mod logs are disabled when it is empty

### Out of Scope for V1

- Logging role, nickname and channel changes
- Logging bulk deletes (purges)
- Per-server configuration through slash commands
- Storing logs in a database

## 4.2 Events

| Event | discord.py handler | Logged details |
|---|---|---|
| Message deleted | `on_raw_message_delete` | Channel, author, content, attachments |
| Message edited | `on_message_edit` | Channel, author, before, after, jump link |
| Member joined | `on_member_join` | Mention, account created, avatar |
| Member left | `on_member_remove` | Mention, joined date, avatar |
| Member banned | `on_member_ban` | Mention, banned by, reason, avatar |
| Member unbanned | `on_member_unban` | Mention, unbanned by |

## 4.3 Behaviour

- **Raw delete event.** `on_raw_message_delete` fires even when the message is not in the bot's cache. If the message was sent before the bot last started, its content is unknown and the embed says so.
- **Edit filtering.** `on_message_edit` also fires for link-preview and embed updates. The event is only logged when the message text actually changed.
- **Ignored messages.** Messages from bots, DMs, and messages in the mod-log channel itself are not logged, so the bot never logs its own posts.
- **Field limits.** Embed field values are capped at 1024 characters, so long content is truncated with `…`.
- **Audit log lookup.** For bans and unbans the bot checks the 5 most recent matching audit log entries for the target user. Without the View Audit Log permission, the "by" and "reason" fields are left out.

## 4.4 Requirements

- **Intents:** Server Members (joins/leaves) and Message Content (message text)
- **Permissions in the mod-log channel:** View Channel, Send Messages, Embed Links
- **Server permission:** View Audit Log (for ban/unban moderator and reason)

## 4.5 Console Logging

The bot writes operational logs to the terminal using Python's `logging` module:

- On startup it reports whether mod logs are enabled, and whether the bot can send, embed and read the audit log
- A warning when the mod-log channel is missing or the bot cannot post in it
- A warning when the audit log cannot be read
