import discord
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

from utils.data_utils import fetch_data
from utils.general_utils import get_distance_from_target, create_embed, truncate_string
from utils.types import BaseCommand, CityData, ClosestCitySearchTypes


class ClosestCityToTarget(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict, server_settings: dict):
        super().__init__(ctx, params, server_settings)

    async def command_logic(self):
        entity_type = self.command_params.get('search_type')  # 'player' or 'alliance'
        entity_name = self.command_params.get('name')  # player_name or alliance_name

        try:
            target_coords = tuple(map(int, self.command_params.get('coords').split(':')))

        except ValueError:
            raise ValueError(f"Invalid coordinates format: {self.command_params.get('coords')}. Expected format 'X:Y'.")

        if entity_type == ClosestCitySearchTypes.PLAYER:
            embed = self.fetch_cities_for_player(entity_name, target_coords)
        else:
            embed = self.fetch_cities_for_alliance(entity_name, target_coords)

        # noinspection PyUnresolvedReferences
        await self.ctx.response.send_message(embed=embed)

    def fetch_cities_for_player(self, entity_name, target_coords):
        # Fetch cities for a single player
        cities_data = fetch_data(
            f"server={self.region_id}&world={self.world_id}&state=&search=city&nick={entity_name}", entity_name)

        if not cities_data:
            raise ValueError(f"Could not fetch cities data for player {entity_name}!")

        closest_city = self.get_closest_city(cities_data, target_coords)
        return self.get_player_result_as_embed(closest_city, target_coords)

    def fetch_cities_for_alliance(self, entity_name, target_coords):
        # Fetch cities for all members of an alliance
        alliance_data = fetch_data(f"server={self.region_id}&world={self.world_id}&state=active&search=ally&allies[1]={entity_name}")

        if not alliance_data:
            raise ValueError(f"Could not fetch cities data for alliance {entity_name}!")

        # Find the closest city for each player in the alliance
        closest_cities = sorted(alliance_data, key=lambda city: get_distance_from_target(city.coords, target_coords))[:10]  # Limit to 10 closest cities
        return self.get_alliance_results_as_embed(closest_cities, target_coords)

    def get_closest_city(self, cities_data: list[CityData], target_coords: tuple) -> CityData:
        """Helper method to find the closest city to target coordinates."""
        return min(cities_data, key=lambda city: get_distance_from_target(city.coords, target_coords))

    def get_player_result_as_embed(self, closest_city: CityData, target_coords: tuple) -> discord.Embed:
        """Generate embed for closest city result."""

        # Create table with table2ascii
        table_content = t2a(
            header=["Coords", "City Name", "Owner", f"Distance"],
            body=[self.get_city_as_table_row(closest_city, target_coords)],
            style=PresetStyle.thick_compact,
            alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER]
        )

        embed = create_embed(description=f"Found the closest city to coordinates **{self.command_params.get('coords')}**")
        embed.add_field(name="", value=f"```\n{table_content}\n```", inline=False)

        return embed

    def get_alliance_results_as_embed(self, closest_cities: list[CityData], target_coords: tuple) -> discord.Embed:
        """Generate embed for closest cities in an alliance."""
        embed = create_embed(description=f"Found the closest cities in alliance **{str(self.command_params.get('name')).capitalize()}** to coordinates **{self.command_params.get('coords')}**")

        # Prepare data for the table
        table_data = []

        for city in closest_cities:
            table_data.append(self.get_city_as_table_row(city, target_coords))

        # Create table with table2ascii
        table_content = t2a(
            header=["Coords", "City Name", "Owner", f"Distance"],
            body=table_data,
            style=PresetStyle.thick_compact,
            alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER]
        )

        # Add the table content to the embed
        embed.add_field(name="", value=f"```\n{table_content}\n```", inline=False)

        return embed

    def get_city_as_table_row(self, city: CityData, target_coords) -> list[str]:
        distance_to_target = int(get_distance_from_target(city.coords, target_coords))
        city_name = truncate_string(city.city_name, 10)
        player_name = truncate_string(city.player_name, 10)

        # Append row data
        return [
            f"{city.coords[0]}:{city.coords[1]}",  # Coords as string
            f"{city_name}",
            f"{player_name}",
            f"{distance_to_target}"
        ]
