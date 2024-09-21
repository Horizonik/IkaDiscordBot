import discord

from utils.types import BaseCommand, CityInfo
from utils.utils import fetch_data, get_closest_city_to_target


class ClosestCityToTarget(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)
        self.command_params = params

    async def command_logic(self):
        cities_data = fetch_data(f"state=&search=city&nick={self.command_params['player_name']}")

        # Filter out any startsWith matches, only exact name matches will remain
        cities_data = [city for city in cities_data if city.player_name == self.command_params['player_name']]

        try:
            target_coords = tuple(map(int, self.command_params.get('coords').split(':')))
        except ValueError:
            raise ValueError(f"Invalid coordinates format: {self.command_params.get('coords')}. Expected format 'X:Y'.")

        # Find the city closest to the target coordinates
        closest_city = min(cities_data, key=lambda city: get_closest_city_to_target(city.coords, target_coords))

        # Sort cities by their coordinates (this might not be necessary, as you're searching by distance)
        cities_data.sort(key=lambda city: (city.coords[0], city.coords[1]))

        # Do something with the closest_city (e.g., return it, use it further in logic)
        embed = self.get_result_as_embed(closest_city, target_coords)
        await self.ctx.response.send_message(embed=embed)

    def get_result_as_embed(self, closest_city: CityInfo, target_coords: tuple) -> discord.Embed:
        # Create a Discord embed for the closest city
        embed = discord.Embed(
            description=f"Found the closest city to coordinates **{self.command_params.get('coords')}**",
            color=discord.Color.blue()
        )

        # Adding fields to the embed with city information
        embed.add_field(name="City Name", value=closest_city.city_name, inline=True)
        embed.add_field(name="City Coordinates", value=f"{closest_city.coords[0]}:{closest_city.coords[1]}", inline=True)
        embed.add_field(name="Player", value=closest_city.player_name, inline=True)
        embed.add_field(name="Distance to Target", value=f"{int(get_closest_city_to_target(closest_city.coords, target_coords))}", inline=True)

        # Optionally set an author or footer if needed
        embed.set_author(name=self.command_params['player_name'])

        return embed
