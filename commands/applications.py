import discord
from discord.ui import Modal, TextInput
from datetime import datetime
from config import APPLICATIONS_FILE, TICKET_CATEGORY_ID, STAFF_ROLE_ID, REGISTRATION_FILE, STAFF_LOG_CHANNEL_ID
from utils.file_utils import save_application, load_file
from utils.logging_utils import log_message


def setup(bot):
    @bot.tree.command(name="apply", description="Submit an application to join the server.")
    async def apply(interaction: discord.Interaction):
        registrations = load_file(REGISTRATION_FILE)

        # Check if the user has registered their SteamID64
        steam_id = registrations.get(str(interaction.user.id))
        if not steam_id:
            await interaction.response.send_message(
                "You need to register your SteamID64 first. Use `/register` to register.", ephemeral=True
            )
            return

        # Define the application form
        class ApplicationForm(Modal, title="Server Application Form"):
            why_play = TextInput(
                label="Why do you want to join the server?",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=500,
            )
            experience = TextInput(
                label="What experience do you have on servers?",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=500,
            )

            async def on_submit(self, interaction: discord.Interaction):
                # Save the application data
                application_data = {
                    "user_id": interaction.user.id,
                    "username": str(interaction.user),
                    "steam_id": steam_id,
                    "why_play": self.why_play.value,
                    "experience": self.experience.value,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                save_application(application_data, APPLICATIONS_FILE)

                guild = interaction.guild
                category = guild.get_channel(TICKET_CATEGORY_ID)

                try:
                    # Attempt to create the ticket channel
                    ticket_channel = await guild.create_text_channel(
                        name=f"ticket-{interaction.user.display_name}",
                        category=category,
                        overwrites={
                            guild.default_role: discord.PermissionOverwrite(view_channel=False),
                            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                            discord.utils.get(guild.roles, id=STAFF_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
                        },
                    )

                    # Send confirmation and initial message
                    await ticket_channel.send(
                        f"Thank you for your application, {interaction.user.mention}!\n"
                        f"A staff member will review your application shortly.\n\n"
                        f"**Application Details:**\n"
                        f"- **Why Play:** {self.why_play.value}\n"
                        f"- **Experience:** {self.experience.value}"
                    )

                    await interaction.response.send_message(
                        f"Your application has been submitted. Please proceed to {ticket_channel.mention} for further communication.",
                        ephemeral=True,
                    )

                    # Log the application creation
                    await log_message(
                        bot,
                        "New Application Created",
                        (
                            f"**User:** <@{interaction.user.id}> (`{interaction.user}`)\n"
                            f"**SteamID64:** `{steam_id}`\n"
                            f"**Why Play:** {self.why_play.value}\n"
                            f"**Experience:** {self.experience.value}\n"
                            f"**Ticket Channel:** {ticket_channel.mention}"
                        ),
                        discord.Color.blue(),
                        log_channel_id=STAFF_LOG_CHANNEL_ID
                    )

                except discord.errors.Forbidden:
                    # Handle missing permissions
                    await interaction.response.send_message(
                        "The bot lacks the necessary permissions to create a ticket channel. Please contact an admin.",
                        ephemeral=True,
                    )
                    await log_message(
                        bot,
                        "Permission Error",
                        f"The bot failed to create a ticket channel due to insufficient permissions in category `{category.name}`.",
                        discord.Color.red(),
                        log_channel_id=STAFF_LOG_CHANNEL_ID
                    )

        # Show the application form
        await interaction.response.send_modal(ApplicationForm())
