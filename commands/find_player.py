from embeds.embeds import find_player_embed
from utils.data_utils import fetch_data
from utils.types import BaseCommand


class FindPlayer(BaseCommand):

    async def command_logic(self):
        """
        Find all cities of a player in a given alliance.

        Raises:
            ValueError: If the player name is too short or too long.
        """

        alliance_name = self.command_params['alliance_name']
        player_name = self.command_params['player_name']

        if len(player_name) < 3 or len(player_name) > 18:
            raise ValueError(f"a player that goes by the name of '{player_name}' doesn't exist!")

        cities_data = fetch_data(
            f"server={self.region_id}&world={self.world_id}&state=&search=city&nick={player_name}{f'&ally={alliance_name}' if alliance_name else ''}",
            self.command_params['player_name']
        )

        # Sort cities by their coordinates
        cities_data.sort(key=lambda city: (city.coords[0], city.coords[1]))
        await self.ctx.response.send_message(embed=find_player_embed(cities_data, player_name, self.world_id, self.region_id))
