import discord

from embeds.embeds import closest_player_city_to_target_embed, closest_alliance_member_to_target_embed
from utils.data_utils import fetch_data
from utils.general_utils import get_distance_from_target
from utils.math_utils import get_closest_city
from utils.types import BaseCommand, ClosestCitySearchTypes


class ClosestCityToTarget(BaseCommand):

    async def command_logic(self):
        entity_type = self.command_params.get('search_type')  # 'player' or 'alliance'
        entity_name = self.command_params.get('name')  # player_name or alliance_name

        try:
            target_coords = tuple(map(int, self.command_params.get('coords').split(':')))
        except ValueError:
            raise ValueError(f"Invalid coordinates format: {self.command_params.get('coords')}. Expected format 'X:Y'.")

        if entity_type == ClosestCitySearchTypes.PLAYER:
            embed = self.fetch_cities_for_player(entity_name, target_coords)
        elif entity_type == ClosestCitySearchTypes.ALLIANCE:
            embed = self.fetch_cities_for_alliance(entity_name, target_coords)
        else:
            raise ValueError(f"I don't know how you managed to search for {entity_name}, you can only search for 'player' or 'alliance'.")

        await self.ctx.response.send_message(embed=embed)

    def fetch_cities_for_player(self, player_name: str, target_coords: tuple) -> discord.Embed:
        """Fetch and calculate which of the player's cities is the closest to the provided coords"""

        cities_data = fetch_data(f"server={self.region_id}&world={self.world_id}&state=&search=city&nick={player_name}", player_name)
        if not cities_data:
            raise ValueError(f"Could not fetch cities data for player {player_name}!")

        closest_city = get_closest_city(cities_data, target_coords)
        return closest_player_city_to_target_embed(closest_city, target_coords)

    def fetch_cities_for_alliance(self, alliance_name: str, target_coords: tuple) -> discord.Embed:
        """Fetch and calculate which alliance member city is the closest to the provided coords"""

        alliance_data = fetch_data(f"server={self.region_id}&world={self.world_id}&state=active&search=ally&allies[1]={alliance_name}")
        if not alliance_data:
            raise ValueError(f"could not fetch cities data for alliance {alliance_name}! Are you sure it exists?")

        closest_cities = sorted(alliance_data, key=lambda city: get_distance_from_target(city.coords, target_coords))[:10]  # Limit to 10 closest cities
        return closest_alliance_member_to_target_embed(closest_cities, target_coords, alliance_name)
