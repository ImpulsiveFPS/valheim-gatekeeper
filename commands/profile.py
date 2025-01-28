import discord
from discord import app_commands
from datetime import datetime
from pathlib import Path
import yaml
from config import (
    REGISTRATION_FILE,
    WHITELIST_FILE,
    VIP_FILE,
    WARD_DATA_FILE,
    PORTAL_DATA_FILE,
    PLAYER_STATS_FILE,
    CHARACTER_SAVE_PATH,
)
from utils.file_utils import load_file


def setup(bot):
    @bot.tree.command(name="profile", description="Show your Valheim server profile.")
    async def profile(interaction: discord.Interaction, user: discord.Member = None):
        # Default to the command user if no target user is specified
        registrations = load_file(REGISTRATION_FILE)
        target_user = user or interaction.user
        steam_id = registrations.get(str(target_user.id))

        if not steam_id:
            await interaction.response.send_message(
                f"{target_user.mention} has not registered their SteamID64. Use `/register` to register first.",
                ephemeral=True,
            )
            return

        # Load data
        whitelist = load_file(WHITELIST_FILE)
        vip_list = load_file(VIP_FILE)
        ward_data = load_file(WARD_DATA_FILE)

        # Parse the portal file
        portal_data = {}
        try:
            with open(PORTAL_DATA_FILE, "r") as f:
                for line in f:
                    if ":" in line:
                        key, value = line.strip().split(":")
                        portal_data[key.strip()] = int(value.strip())
        except FileNotFoundError:
            await interaction.response.send_message(
                "Portal data file is missing. Unable to retrieve portal information.", ephemeral=True
            )
            return

        # Get Ward and Portal Counts
        ward_count = ward_data.get(steam_id, 0)
        portal_count = portal_data.get(steam_id, 0)

        # Determine Whitelist and VIP Status
        is_whitelisted = steam_id in whitelist
        is_vip = steam_id in vip_list

        # Get Character Name and Last Played
        character_name = None
        last_played = None
        for file in Path(CHARACTER_SAVE_PATH).glob(f"Steam_{steam_id}_*"):
            character_name = file.stem.split("_", 2)[-1]
            last_played = datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
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
