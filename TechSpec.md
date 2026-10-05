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
| Mod logs | Planned | Deletes, edits, joins/leaves, bans |
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

