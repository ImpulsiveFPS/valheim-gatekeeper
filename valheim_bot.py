import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path
import json
import aiohttp  # For webhook support
from discord.ui import View, Button
import yaml  # For parsing PlayerListData.yml
import os  # For retrieving file modification times
from datetime import datetime  # For formatting the last played timestamp

# File paths
WHITELIST_FILE = r"WHITELIST_FILE_PATH\Saves\permittedlist.txt" # Permitted list. Found where the server saves it´s world
VIP_FILE = r"VIP_FILE_PATH" # Requires Arcane Ward by KG to function
VIP_PORTAL_FILE = r"VIP2_FILE_PATH" # Requires RareMagicPortalPlus By WackyMole to function
REGISTRATION_FILE = r"PATH_TO_SAVE_STEAMID64s_user_registrations.json" # Path where you want to save the registered data from players.
CHARACTER_SAVE_PATH = r"PATH_TO_SERVERCHARACTERS_SAVE_FOLDER\Saves\characters_local" # Requires Servercharacters By Smoothbrain to function
PLAYER_STATS_FILE = r"PATH_TO_ALMANACC_PLAYER_STATS\BepInEx\config\Almanac\Players\PlayerListData.yml" # Requires Almanac By RustyMods to function
WARD_DATA_FILE = r"PATH_TO_ARCANEWARD_WARDDATA\BepInEx\config\ArcaneWard\WardData.json" # Requires Arcane Ward by KG to function
PORTAL_DATA_FILE = r"PATH_TO_RMP_PORTALDATA\BepInEx\config\Portal_Names\PoweredByAMP_PlayerPortals.json" # Requires RareMagicPortalPlus By WackyMole to function

# Discord bot setup
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Role IDs
WHITELIST_ROLE_ID = WHITELISTED_ROLE  # Whitelist role ID
VIP_ROLE_ID = VIP_ROLE        # VIP role ID
STAFF_ROLE_ID = ID_STAFF_ROLE # Staff role ID so that staff members can register steamid64 of other users and handle applications

# Logging configuration
LOG_CHANNEL_ID = LOG_CHANNEL  # Log channel ID


# Helper Functions
def load_file(file_path):
    """Load data from a JSON or text file."""
    try:
        if file_path.endswith(".json"):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            with open(file_path, "r") as f:
                return f.read().splitlines()
    except (FileNotFoundError, json.JSONDecodeError):
        return [] if not file_path.endswith(".json") else {}


def save_file(file_path, data):
    """Save data to a JSON or text file."""
    file_dir = Path(file_path).parent
    file_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    if file_path.endswith(".json"):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    else:
        with open(file_path, "w") as f:
            f.writelines(f"{entry}\n" for entry in sorted(set(data)))


async def log_message(title, description, color=discord.Color.blue()):
    """Send a log message as an embed."""
    embed = discord.Embed(title=title, description=description, color=color)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)


# Event: Bot Ready
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}.")
    await log_message("Bot Online", f"Bot is online and ready. Logged in as `{bot.user}`.")


# Event: Role Updates
@bot.event
async def on_member_update(before, after):
    registrations = load_file(REGISTRATION_FILE)
    steam_id = registrations.get(str(after.id))
    if not steam_id:
        return

    before_roles = {role.id for role in before.roles}
    after_roles = {role.id for role in after.roles}

    whitelist = load_file(WHITELIST_FILE)
    vip_list = load_file(VIP_FILE)
    vip_portal_list = load_file(VIP_PORTAL_FILE)

    # VIP role added
    if VIP_ROLE_ID in after_roles and VIP_ROLE_ID not in before_roles:
        if WHITELIST_ROLE_ID not in after_roles:
            whitelist_role = discord.utils.get(after.guild.roles, id=WHITELIST_ROLE_ID)
            if whitelist_role:
                await after.add_roles(whitelist_role)
                await log_message(
                    "Role Added",
                    f"Whitelist role added to **<@{after.id}>** due to VIP role.",
                    discord.Color.green()
                )
        vip_list.append(steam_id)
        vip_portal_list.append(steam_id)
        save_file(VIP_FILE, vip_list)
        save_file(VIP_PORTAL_FILE, vip_portal_list)
        await log_message(
            "Added to VIP",
            f"**<@{after.id}>** was added to the VIP list and VIP portal list.",
            discord.Color.green()
        )

    # VIP role removed
    if VIP_ROLE_ID not in after_roles and steam_id in vip_list:
        vip_list.remove(steam_id)
        vip_portal_list.remove(steam_id)
        save_file(VIP_FILE, vip_list)
        save_file(VIP_PORTAL_FILE, vip_portal_list)
        await log_message(
            "Removed from VIP",
            f"**<@{after.id}>** was removed from the VIP list and VIP portal list.",
            discord.Color.red()
        )

    # Whitelist role added
    if WHITELIST_ROLE_ID in after_roles and steam_id not in whitelist:
        whitelist.append(steam_id)
        save_file(WHITELIST_FILE, whitelist)
        await log_message(
            "Added to Whitelist",
            f"**<@{after.id}>** was added to the whitelist.",
            discord.Color.green()
        )

    # Whitelist role removed
    if WHITELIST_ROLE_ID not in after_roles and steam_id in whitelist:
        whitelist.remove(steam_id)
        save_file(WHITELIST_FILE, whitelist)
        await log_message(
            "Removed from Whitelist",
            f"**<@{after.id}>** was removed from the whitelist.",
            discord.Color.red()
        )


# Event: User Leaves the Server
@bot.event
async def on_member_remove(member):
    registrations = load_file(REGISTRATION_FILE)
    steam_id = registrations.pop(str(member.id), None)

    if steam_id:
        whitelist = load_file(WHITELIST_FILE)
        vip_list = load_file(VIP_FILE)
        vip_portal_list = load_file(VIP_PORTAL_FILE)

        if steam_id in whitelist:
            whitelist.remove(steam_id)
            save_file(WHITELIST_FILE, whitelist)

        if steam_id in vip_list:
            vip_list.remove(steam_id)
            save_file(VIP_FILE, vip_list)

        if steam_id in vip_portal_list:
            vip_portal_list.remove(steam_id)
            save_file(VIP_PORTAL_FILE, vip_portal_list)

        save_file(REGISTRATION_FILE, registrations)

        await log_message(
            "User Left Server",
            f"**User:** <@{member.id}> removed from all lists.\n**SteamID64:** `{steam_id}`",
            discord.Color.red()
        )


# Slash Command: /register
@bot.tree.command(name="register", description="Register your SteamID64.")
async def register(interaction: discord.Interaction, steam_id: str):
    if not steam_id.isdigit() or len(steam_id) != 17:
        await interaction.response.send_message("Invalid SteamID64. Must be a 17-digit number.", ephemeral=True)
        return
    registrations = load_file(REGISTRATION_FILE)
    registrations[str(interaction.user.id)] = steam_id
    save_file(REGISTRATION_FILE, registrations)
    await interaction.response.send_message(f"SteamID64 `{steam_id}` registered successfully.", ephemeral=True)
    await log_message(
        "Registered",
        f"**User:** <@{interaction.user.id}> registered SteamID64 `{steam_id}`.",
        discord.Color.green()
    )


# Slash Command: /unregister
@bot.tree.command(name="unregister", description="Unregister your SteamID64.")
async def unregister(interaction: discord.Interaction):
    registrations = load_file(REGISTRATION_FILE)
    discord_id = str(interaction.user.id)
    if discord_id not in registrations:
        await interaction.response.send_message("You are not registered.", ephemeral=True)
        return

    # Warn the user about the consequences
    embed = discord.Embed(
        title="Unregister Confirmation",
        description=(
            "Are you sure you want to unregister your SteamID64?\n\n"
            "This action will:\n"
            "- Remove you from the whitelist.\n"
            "- Kick you from the server if you are online.\n"
            "- Prevent you from logging into the Valheim server until you re-apply for whitelisting."
        ),
        color=discord.Color.red()
    )

    # Confirmation View
    class ConfirmUnregisterView(View):
        def __init__(self):
            super().__init__()
            self.value = None

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: Button):
            registrations = load_file(REGISTRATION_FILE)
            steam_id = registrations.pop(discord_id)
            save_file(REGISTRATION_FILE, registrations)

            # Remove the user's SteamID64 from the whitelist file
            whitelist = load_file(WHITELIST_FILE)
            if steam_id in whitelist:
                whitelist.remove(steam_id)
                save_file(WHITELIST_FILE, whitelist)

            # Remove the whitelist role from the user, if they have it
            whitelist_role = discord.utils.get(interaction.guild.roles, id=WHITELIST_ROLE_ID)
            if whitelist_role in interaction.user.roles:
                await interaction.user.remove_roles(whitelist_role)

            # Respond to the interaction and log the action
            await interaction.response.send_message(
                f"SteamID64 `{steam_id}` unregistered successfully. You have been removed from the whitelist.",
                ephemeral=True
            )
            await log_message(
                "Unregistered",
                f"**User:** <@{interaction.user.id}> unregistered SteamID64 `{steam_id}` and was removed from the whitelist.",
                discord.Color.red()
            )

        @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            await interaction.response.send_message(
                "Unregister action canceled.", ephemeral=True
            )

    # Send the confirmation message
    view = ConfirmUnregisterView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Slash Command: /register_user
@bot.tree.command(name="register_user", description="Register another user's SteamID64.")
async def register_user(interaction: discord.Interaction, user: discord.Member, steam_id: str):
    # Check if the invoking user has the required role
    required_role_id = STAFF_ROLE_ID
    has_role = any(role.id == required_role_id for role in interaction.user.roles)

    if not has_role:
        await interaction.response.send_message(
            "You do not have the required role to use this command.", ephemeral=True
        )
        return

    # Validate SteamID64
    if not steam_id.isdigit() or len(steam_id) != 17:
        await interaction.response.send_message("Invalid SteamID64. Must be a 17-digit number.", ephemeral=True)
        return

    # Register the SteamID64 for the specified user
    registrations = load_file(REGISTRATION_FILE)
    registrations[str(user.id)] = steam_id
    save_file(REGISTRATION_FILE, registrations)
    await interaction.response.send_message(
        f"SteamID64 `{steam_id}` registered successfully for {user.mention}.", ephemeral=True
    )
    await log_message(
        "Registered by User",
        f"**User:** <@{interaction.user.id}> registered SteamID64 `{steam_id}` for **{user.mention}**.",
        discord.Color.green()
    )

# Slash Command: /profile
@bot.tree.command(name="profile", description="Show your Valheim server profile based on your Discord account.")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    registrations = load_file(REGISTRATION_FILE)

    # Default to the command user if no target user is specified
    target_user = user or interaction.user
    steam_id = registrations.get(str(target_user.id))

    if not steam_id:
        await interaction.response.send_message(
            f"{target_user.mention} has not registered their SteamID64. Use `/register` to register first.",
            ephemeral=True
        )
        return

    # Load data
    whitelist = load_file(WHITELIST_FILE)
    vip_list = load_file(VIP_FILE)
    ward_data = load_file(WARD_DATA_FILE)

    # Parse the portal file (specific format with `:` delimiter)
    portal_data = {}
    try:
        with open(PORTAL_DATA_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(":")
                    portal_data[key.strip()] = int(value.strip())
    except FileNotFoundError:
        await log_message("Error", f"Portal data file `{PORTAL_DATA_FILE}` not found.", discord.Color.red())

    # Get Ward and Portal Counts
    ward_count = ward_data.get(steam_id, 0)
    portal_count = portal_data.get(steam_id, 0)

    # Determine Whitelist and VIP Status
    is_whitelisted = steam_id in whitelist
    is_vip = steam_id in vip_list

    # Get Character Name
    character_name = None
    last_played = None
    for file in Path(CHARACTER_SAVE_PATH).glob(f"Steam_{steam_id}_*"):
        character_name = file.stem.split("_", 2)[-1]
        last_played = datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')  # Get last modified date
        break

    # Load Player Stats
    stats = None
    try:
        with open(PLAYER_STATS_FILE, "r", encoding="utf-8") as f:
            stats_data = yaml.safe_load(f)
            if character_name in stats_data:
                stats = stats_data[character_name]
    except (FileNotFoundError, yaml.YAMLError):
        pass

    # Prepare the embed
    embed = discord.Embed(title=f"Profile for {target_user.display_name}", color=discord.Color.green())
    embed.add_field(name="SteamID64", value=steam_id, inline=False)
    embed.add_field(name="Whitelisted", value="Yes" if is_whitelisted else "No", inline=True)
    embed.add_field(name="VIP", value="Yes" if is_vip else "No", inline=True)
    embed.add_field(name="Wards", value=str(ward_count), inline=True)
    embed.add_field(name="Portals", value=str(portal_count), inline=True)
    embed.add_field(name="Character Name", value=character_name or "Not Found", inline=False)
    embed.add_field(name="Last Played", value=last_played or "Not Found", inline=False)

    if stats:
        embed.add_field(name="Completed Achievements", value=str(stats.get("completed_achievements", 0)), inline=True)
        embed.add_field(name="Total Kills", value=str(stats.get("total_kills", 0)), inline=True)
        embed.add_field(name="Total Deaths", value=str(stats.get("total_deaths", 0)), inline=True)
    else:
        embed.add_field(name="Player Stats", value="No stats available.", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Run the bot
bot.run("DISCORD_BOT_TOKEN")  # Replace with your bot token
