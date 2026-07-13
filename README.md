# 🚔 SAPD PagerDispatch Bot

A production-ready Discord bot for SA-MP roleplay police department dispatch operations.

## Features

- 🚨 Quick dispatch creation with modal forms
- 📍 Real-time officer status tracking (Responding, En Route, On Scene, Command)
- ⚫ Specialized unit selection (SWAT, Detectives, Traffic Division)
- 🆔 Automatic dispatch numbering
- 👮 Role-based permissions
- 📊 SQLite logging and persistence
- 🔔 Panic alarm system
- 💾 Persistent Discord views (survives bot restarts)

## Technology Stack

- Python 3.12+
- discord.py 2.x
- SQLite + aiosqlite
- python-dotenv
- Modular Cog Architecture

## Installation

### Prerequisites
- Python 3.12 or higher
- Discord bot token
- Administrator access to a Discord server

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/GrigMax1/pagerdispatch.git
cd pagerdispatch
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```
Edit `.env` and add your bot token:
```
DISCORD_TOKEN=your_token_here
```

5. **Configure the bot:**
Edit `config.json` with your server details:
```json
{
  "guild_id": YOUR_SERVER_ID,
  "dispatch_channel_id": YOUR_DISPATCH_CHANNEL_ID,
  "dispatch_console_channel_id": YOUR_CONSOLE_CHANNEL_ID,
  "log_channel_id": YOUR_LOG_CHANNEL_ID,
  "police_role_id": YOUR_POLICE_ROLE_ID,
  "swat_role_id": YOUR_SWAT_ROLE_ID,
  "detective_role_id": YOUR_DETECTIVE_ROLE_ID,
  "traffic_role_id": YOUR_TRAFFIC_ROLE_ID,
  "supervisor_role_ids": [YOUR_SUPERVISOR_ROLE_IDS],
  "department_logo_url": "https://example.com/logo.png",
  "embed_color": 15158332,
  "footer_text": "SAPD Dispatch System",
  "timezone": "America/Los_Angeles"
}
```

6. **Initialize the database:**
```bash
python -c "from database.database import Database; import asyncio; asyncio.run(Database().initialize())"
```

7. **Run the bot:**
```bash
python bot.py
```

## Discord Setup

### Create the Bot Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**, name it "SAPD PagerDispatch"
3. Go to **Bot** tab, click **Add Bot**
4. Copy the token and paste into `.env`
5. Under **TOKEN**, click **Copy** (use this in `.env`)

### Configure Bot Permissions

1. Go to **OAuth2** → **URL Generator**
2. Select scopes: `bot`
3. Select permissions:
   - `Send Messages`
   - `Send Messages in Threads`
   - `Embed Links`
   - `Attach Files`
   - `Read Message History`
   - `Mention @everyone, @here, and All Roles`
4. Copy the generated URL and invite the bot to your server

### Discord Server Setup

1. Create a category named "DISPATCH"
2. Create channels:
   - `#dispatch-console` (Dispatch Console Channel)
   - `#active-dispatches` (Dispatch Channel)
   - `#logs` (Log Channel)
3. Create roles:
   - Police Officer
   - SWAT
   - Detective Bureau
   - Traffic Division
   - Supervisors (Sergeant+)
4. Update `config.json` with these IDs

## Usage

### Initial Setup (Admin Only)

Run the setup command **once** in the dispatch console channel:
```
/setup_dispatch
```

This creates the permanent Dispatch Console with buttons.

### Creating Dispatches

1. Click **🚨 Create Dispatch** on the console
2. Select dispatch category
3. Fill in the modal (Title, Location, Situation)
4. Select required specialized units
5. Dispatch is created and appropriate roles are mentioned

### Panic Alarm

Click **🚨 Panic Alarm** to instantly create an emergency dispatch with:
- Title: `PANIC ALARM`
- Auto-selects SWAT
- Mentions Police and SWAT roles

### Officer Response

Officers click dispatch buttons to update their status:
- ✅ **Responding** - Acknowledgement
- 🚓 **En Route** - Moving to scene
- 📍 **On Scene** - Arrived at location
- 👮 **Taking Command** - Assumed command
- ❌ **Unable** - Cannot respond
- 🔒 **Close Dispatch** - Supervisors only

### Closing Dispatches

Only supervisors can close active dispatches with the **🔒 Close Dispatch** button.

## Project Structure

```
pagerdispatch/
├── bot.py                          # Main bot file
├── config.py                       # Configuration loader
├── config.json                     # Configuration file
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── README.md                       # This file
├── cogs/
│   ├── dispatch.py                # Dispatch management cog
│   ├── setup.py                   # Setup command cog
│   └── logging.py                 # Logging cog
├── views/
│   ├── dispatch_console.py        # Dispatch console view
│   ├── dispatch_buttons.py        # Officer response buttons
│   └── modals.py                  # Input modals
├── database/
│   ├── database.py                # Database manager
│   └── schema.sql                 # SQLite schema
└── utils/
    ├── permissions.py             # Permission checking
    ├── helpers.py                 # Helper functions
    └── embeds.py                  # Embed builders
```

## Database Schema

### dispatches table
- `dispatch_id` (INTEGER PRIMARY KEY)
- `dispatch_number` (TEXT UNIQUE)
- `category` (TEXT)
- `title` (TEXT)
- `location` (TEXT)
- `situation` (TEXT)
- `created_by` (TEXT)
- `created_at` (DATETIME)
- `status` (TEXT) - Active, Closed
- `swat_required` (BOOLEAN)
- `detectives_required` (BOOLEAN)
- `traffic_required` (BOOLEAN)
- `message_id` (INTEGER UNIQUE)

### dispatch_logs table
- `log_id` (INTEGER PRIMARY KEY)
- `dispatch_id` (INTEGER)
- `action` (TEXT)
- `user_name` (TEXT)
- `timestamp` (DATETIME)

### bot_settings table
- `setting_key` (TEXT PRIMARY KEY)
- `setting_value` (TEXT)

## Logging

All actions are logged to SQLite and optionally mirrored to Discord:
- Dispatch created
- Dispatch closed
- Panic alarm activated
- Officer responding/en route/on scene/command/unable
- Unit selection changes

## Permissions

| Action | Required Role |
|--------|---------------|
| Create Dispatch | Officer+ |
| Use Panic Alarm | Officer+ |
| Close Dispatch | Supervisor+ |
| Setup Console | Server Admin |

## Troubleshooting

### Bot not responding to commands
- Ensure bot has message permissions in the channel
- Check that the bot role is above command-issuer role
- Verify bot token is correct in `.env`

### Buttons not working
- Bot must be running to process interactions
- Check bot permissions in Discord server
- Ensure views are properly loaded on bot restart

### Database errors
- Delete `dispatch.db` and run initialization again
- Check file permissions in the project directory

## Support

For issues or feature requests, open an issue on GitHub.

## License

MIT License - See LICENSE file for details

## Author

Created for SA-MP roleplay communities
