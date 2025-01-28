
# Valheim Gatekeeper
A Discord bot designed to manage applications, automate whitelisting by role, and handle VIP player privileges for Valheim servers.

## Features

Valheim Gatekeeper integrates with popular Valheim mods to provide powerful functionality, including:

### **Ward Count & VIP Wards**
- Tracks the number of wards built by a player.
- Manages VIP player privileges, allowing them to build more wards.
- **Required Mod:** [Arcane Ward](https://thunderstore.io/c/valheim/p/KGvalheim/Arcane_Ward/)

### **Portal Count & VIP Portals**
- Monitors the number of portals created by players.
- Grants VIP players the ability to build more portals.
- **Required Mod:** [Rare Magic Portal Plus](https://thunderstore.io/c/valheim/p/WackyMole/RareMagicPortalPlus/)

### **Player Stats**
- Displays detailed player statistics, including:
  - Total deaths
  - Total kills
  - Completed achievements.
- **Required Mod:** [Almanac](https://thunderstore.io/c/valheim/p/RustyMods/Almanac/)

### **Player Identification & Last Online**
- Identifies player characters by name.
- Displays the last time the player was online.
- **Required Mod:** [ServerCharacters](https://thunderstore.io/c/valheim/p/Smoothbrain/ServerCharacters/)

---

## Prerequisites
To enable full functionality, Valheim Gatekeeper requires the following Valheim mods to be installed on your server:
1. [Arcane Ward](https://thunderstore.io/c/valheim/p/KGvalheim/Arcane_Ward/) – For ward tracking and VIP wards.
2. [Rare Magic Portal Plus](https://thunderstore.io/c/valheim/p/WackyMole/RareMagicPortalPlus/) – For portal tracking and VIP portals.
3. [Almanac](https://thunderstore.io/c/valheim/p/RustyMods/Almanac/) – For tracking player stats.
4. [ServerCharacters](https://thunderstore.io/c/valheim/p/Smoothbrain/ServerCharacters/) – For identifying player names and last online times.

---

## Setup Instructions

### Prerequisites

1. **Python**: Ensure Python 3.10 or higher is installed.
2. **Discord Developer Account**: You need a bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
3. **Valheim Server Files**: The bot interacts with specific files from the Valheim server.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/valheim-discord-bot.git
   cd valheim-discord-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your bot token:
   ```env
   BOT_TOKEN=your_discord_bot_token
   ```

4. Edit the `config.py` file to set your Valheim server paths, role IDs, and category/channel IDs:
   ```python
   # Example for `config.py`
   WHITELIST_FILE = r"C:\PATH\TO\YOUR_VALHEIM_SERVER\Saves\permittedlist.txt"
   VIP_FILE = r"C:\PATH\TO\YOUR_VALHEIM_SERVER\BepInEx\config\ArcaneWard\VIPplayers.txt"
   ...
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

---

## Configuration

The bot’s behavior is controlled via the `config.py` file:

- **Paths to Valheim Server Files**:
  Update paths to match your server setup for:
  - Whitelist (`WHITELIST_FILE`)
  - VIP list (`VIP_FILE`)
  - Wards and portals

- **Role IDs**:
  Update `WHITELIST_ROLE_ID`, `VIP_ROLE_ID`, and `STAFF_ROLE_ID` to match the roles on your server.

- **Category and Channel IDs**:
  - `TICKET_CATEGORY_ID`: Category for tickets.
  - `STAFF_LOG_CHANNEL_ID`: Channel for staff logs.

- **Feature Toggles**:
  Enable or disable specific features:
  ```python
  ENABLE_WARDS = True
  ENABLE_PORTALS = True
  ENABLE_STATS = True
  ENABLE_CHARACTERS = True
  ```

---

## Commands

### User Commands

| Command         | Description                                  |
|------------------|----------------------------------------------|
| `/register`      | Register your SteamID64 for the server.      |
| `/unregister`    | Unregister your SteamID64 and remove roles. |
| `/apply`         | Start an application to join the server.    |
| `/profile`       | View your profile with in-game stats.       |

### Admin Commands

| Command          | Description                                    |
|-------------------|------------------------------------------------|
| `/close_ticket`   | Close a ticket and log the conversation.      |

---

## Logging and Tickets

- **Tickets**: The bot creates a private channel for each application under the ticket category.
- **Logs**: All ticket transcripts and application logs are sent to the staff log channel.

---

## Known Issues

- Ensure the bot has the correct permissions:
  - Manage Roles
  - Manage Channels
  - Read Messages and Message History
  - Send Messages and Embed Links
- Ensure paths to Valheim server files are correct.

---

## Contributing

Feel free to fork the repository and submit pull requests for bug fixes or feature enhancements.

---

## License

This project is licensed under the MIT License.
