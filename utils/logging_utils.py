import discord
from aiohttp import ClientSession


async def log_message(bot, title, description, color=discord.Color.blue(), log_channel_id=None):
    if not log_channel_id:
        return  # Ensure log_channel_id is provided

    channel = bot.get_channel(log_channel_id)
    embed = discord.Embed(title=title, description=description, color=color)

    if channel:
        await channel.send(embed=embed)
    else:
        # If channel isn't available, use webhook (if defined in your config)
        from config import WEBHOOK_URL  # Import here to avoid circular dependency
        if WEBHOOK_URL:
            async with ClientSession() as session:
                webhook_data = {"embeds": [embed.to_dict()]}
                async with session.post(WEBHOOK_URL, json=webhook_data) as response:
                    if response.status != 204:
                        print(f"Failed to send webhook: {response.status}")
