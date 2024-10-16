from embeds.embeds import help_embed
from utils.types import BaseCommand


class HelpCommand(BaseCommand):

    async def command_logic(self):
        await self.ctx.response.send_message(embed=help_embed(self.ctx), ephemeral=True)
