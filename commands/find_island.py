from embeds.embeds import find_island_embed
from utils.data_utils import fetch_data
from utils.types import BaseCommand


class FindIsland(BaseCommand):

    async def command_logic(self):
        """
        Handles the core logic for the find island command.

        Raises:
            ValueError: If the coordinates provided are in an invalid format.
            ValueError: If no cities are found on the island at the specified coordinates.
        """
        # Validate that the coords are in format xx:yy
        try:
            x, y = map(int, self.command_params.get('coords').split(':'))
        except ValueError:
            raise ValueError(f"invalid coordinates format: {self.command_params.get('coords')}. Expected format 'X:Y'.")

        # Fetch the data of the cities present on the selected island
        island_cities_data = fetch_data(f"server={self.region_id}&world={self.world_id}&search=city&x={x}&y={y}")
        if not island_cities_data:
            raise ValueError(f"could not find any cities on the island at {x}:{y}!")

        embed = find_island_embed(island_cities_data, self.world_id, self.region_id)
        await self.ctx.response.send_message(embed=embed)
