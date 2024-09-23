import discord

from utils.general_utils import create_embed
from utils.types import BaseCommand


class HelpCommand(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict, server_settings: dict):
        super().__init__(ctx, params, server_settings)

    async def command_logic(self):
        embed = create_embed("Help Menu", "Here are the commands you can use:")

        # Retrieve and add commands dynamically
        for command in self.ctx.client.tree.get_commands():
            if str.endswith(command.name, "_id"):
                continue

            description = command.description if command.description else "No description available."
            embed.add_field(name=f"/{command.name}", value=description, inline=False)

        await self.ctx.response.send_message(embed=embed, ephemeral=True)
