import discord
from io import StringIO
from config import STAFF_ROLE_ID, STAFF_LOG_CHANNEL_ID
from utils.logging_utils import log_message


def setup(bot):
    @bot.tree.command(name="close_ticket", description="Close the ticket and log the conversation.")
    @discord.app_commands.checks.has_role(STAFF_ROLE_ID)  # Only staff can use this command
    async def close_ticket(interaction: discord.Interaction):
        channel = interaction.channel

        # Ensure the command is used in a ticket channel
        if not channel.name.startswith("ticket-"):
            await interaction.response.send_message(
                "This command can only be used in a ticket channel.", ephemeral=True
            )
            return

        # Transcribe the messages
        transcript = StringIO()
        async for message in channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            author = f"{message.author} (ID: {message.author.id})"
            transcript.write(f"[{timestamp}] {author}: {message.content}\n")

        # Save transcript as a file
        transcript_file = discord.File(
            fp=StringIO(transcript.getvalue()), filename=f"{channel.name}_transcript.txt"
        )

        # Log the transcript to the staff log channel
        log_channel = bot.get_channel(STAFF_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"**Ticket Closed:** {channel.name}\n**Closed by:** {interaction.user.mention}",
                file=transcript_file,
            )

        # Send acknowledgment before deleting the channel
        await interaction.response.send_message(
            "Ticket is being closed and logged.", ephemeral=True
        )

        # Delete the ticket channel
        await channel.delete(reason="Ticket closed by staff.")

    @close_ticket.error
    async def close_ticket_error(interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingRole):
            await interaction.response.send_message(
                "You do not have permission to close tickets.", ephemeral=True
            )
        else:
            # Handle other errors gracefully
            await interaction.response.send_message(
                "An error occurred while closing the ticket. Please try again later.",
                ephemeral=True,
            )

            # Log the error details
            await log_message(
                bot,
                "Ticket Close Error",
                f"Error closing ticket in channel {interaction.channel.name}:\n```{str(error)}```",
                discord.Color.red(),
                log_channel_id=STAFF_LOG_CHANNEL_ID,
            )
