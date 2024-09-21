from itertools import product

import discord

from utils.types import BaseCommand, CityInfo, ClusterInfo
from utils.utils import (
    fetch_data,
    count_cities_per_island,
    convert_data_to_embed
)


class FindPlayer(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)
        self.command_params = params

    async def command_logic(self):
        alliance_name = self.command_params['alliance_name']
        cities_data = fetch_data(
            f"state=&search=city&nick={self.command_params['player_name']}{f'&ally={alliance_name}' if alliance_name else ''}"
        )

        # Filter out any startsWith matches, only exact name matches will remain
        cities_data = [city for city in cities_data if city.player_name == self.command_params['player_name']]

        # Sort cities by their coordinates
        cities_data.sort(key=lambda city: (city.coords[0], city.coords[1]))

        embed = self.create_city_table_embed(cities_data)
        await self.ctx.response.send_message(embed=embed)

        # TODO Produce discord embed

    def create_city_table_embed(self, cities_data: list[CityInfo]) -> discord.Embed:
        embed = discord.Embed(title=f"{self.command_params['player_name']}'s City Information", color=discord.Color.orange())

        # Create the header row
        header = f"{'Coords':<10} {'City Name':<19} {'Resource':<11}\n"
        separator = '-' * 56 + '\n'
        table_rows = ""

        for city in cities_data:
            # Truncate city name if it's longer than 20 characters
            city_name = city.city_name if len(city.city_name) <= 15 else city.city_name[:12] + '..'

            table_rows += (
                f"{str(city.coords):<10} "  # Convert tuple to string
                f"[{city.city_level:<2}] {city_name:<15}"
                f"[{city.island_tradegood:<2}] {city.tradegood_type.capitalize():<7}\n"
            )

        # Combine header, separator, and rows
        table = header + separator + table_rows

        # Add the table to the embed as a code block
        embed.add_field(name="Data", value=f"```\n{table}```", inline=False)

        return embed
