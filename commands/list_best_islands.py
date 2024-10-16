from database.guild_settings_manager import get_islands_data
from embeds.embeds import list_best_islands_embed
from utils.general_utils import rank_islands
from utils.types import BaseCommand


class ListBestIslands(BaseCommand):

    async def command_logic(self):
        islands_data = get_islands_data(self.world_id, self.region_id)
        if not islands_data:
            raise ValueError(
                f"island data is not available for the {str(self.guild_settings['region']).upper()} {str(self.guild_settings['world']).capitalize()} server. Sorry")

        ranked_islands = rank_islands(islands_data, self.command_params['resource_type'], self.command_params['miracle_type'], self.command_params['no_full_islands'])
        await self.ctx.response.send_message(embed=list_best_islands_embed(ranked_islands, self.command_params))
