import discord
from discord import app_commands
from config import REGISTRATION_FILE, WHITELIST_ROLE_ID, VIP_ROLE_ID
from utils.file_utils import load_file, save_file
from utils.logging_utils import log_message

def setup(bot):
    @bot.tree.command(name="register", description="Register your SteamID64.")
    async def register(interaction: discord.Interaction, steam_id: str):
        registrations = load_file(REGISTRATION_FILE)
        registrations[str(interaction.user.id)] = steam_id
        save_file(REGISTRATION_FILE, registrations)
        await interaction.response.send_message(f"SteamID64 `{steam_id}` registered successfully.", ephemeral=True)

    @bot.tree.command(name="unregister", description="Unregister your SteamID64.")
    async def unregister(interaction: discord.Interaction):
        registrations = load_file(REGISTRATION_FILE)
        if str(interaction.user.id) in registrations:
            del registrations[str(interaction.user.id)]
            save_file(REGISTRATION_FILE, registrations)
            await interaction.response.send_message("You have been unregistered.", ephemeral=True)
        else:
            await interaction.response.send_message("You are not registered.", ephemeral=True)
