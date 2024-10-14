import discord
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

from database.guild_settings_manager import get_islands_data
from utils.data_utils import fetch_data
from utils.general_utils import truncate_string, create_embed, get_island_tier
from utils.types import BaseCommand, CityData


class FindPlayer(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict, guild_settings: dict):
        super().__init__(ctx, params, guild_settings)

    async def command_logic(self):
        alliance_name = self.command_params['alliance_name']
        player_name = self.command_params['player_name']

        if len(player_name) < 3 or len(player_name) > 15:
            raise ValueError(f"a player that goes by the name of '{player_name}' doesn't exist!")

        cities_data = fetch_data(
            f"server={self.region_id}&world={self.world_id}&state=&search=city&nick={player_name}{f'&ally={alliance_name}' if alliance_name else ''}",
            self.command_params['player_name']
        )

        # Sort cities by their coordinates
        cities_data.sort(key=lambda city: (city.coords[0], city.coords[1]))

        embed = self.create_city_table_embed(cities_data)
        # noinspection PyUnresolvedReferences
        await self.ctx.response.send_message(embed=embed)

    def create_city_table_embed(self, cities_data: list[CityData]) -> discord.Embed:
        # Load island tier data from the JSON file
        islands_data = get_islands_data(self.world_id, self.region_id)
        embed = create_embed(title=f"{str(self.command_params['player_name']).capitalize()}'s City Information")

        # Prepare data for the table
        table_data = []
        for city in cities_data:
            # Truncate string that might exceed the embed length limit
            city_name = truncate_string(city.city_name, 7)
            wonder_type = truncate_string(city.wonder_type, 6)
            resource_type = truncate_string(city.resource_type, 6)

            # Get the tier of the island
            island_tier = get_island_tier(city.x, city.y, islands_data)

            # Append row data
            table_data.append([
                f"{city.x}:{city.y}",  # Convert tuple to string
                f"[{city.city_level}]{city_name}",
                f"[{city.resource_level}]{resource_type.capitalize()}",
                f"[{city.wonder_level}]{wonder_type.capitalize()}",
                island_tier  # Add island tier to the table
            ])

        # Create table with table2ascii
        table_content = t2a(
            header=["Coords", "City Name", "Resource", "Miracle", "Tier"],
            body=table_data,
            style=PresetStyle.thick_compact,
            alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER]
        )

        # Add the table content to the embed
        embed.add_field(name=f"{len(cities_data)} cities found", value=f"```\n{table_content}\n```", inline=False)

        return embed
