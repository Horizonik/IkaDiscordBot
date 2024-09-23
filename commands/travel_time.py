import math

import discord

from utils.constants import ship_units, unit_speeds
from utils.general_utils import create_embed
from utils.types import BaseCommand


class CalculateTravelTime(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)

    async def command_logic(self):
        unit_type = self.command_params.get('unit_type')
        using_poseidon = self.command_params.get('using_poseidon', False)
        using_oligarchy = self.command_params.get('using_oligarchy', False)
        sea_chart_level = self.command_params.get('sea_chart_level', 0)

        # Validate and parse start coordinates
        try:
            start_x, start_y = map(int, self.command_params['start_coords'].split(':'))
            dest_x, dest_y = map(int, self.command_params['destination_coords'].split(':'))
        except ValueError:
            await self.ctx.response.send_message("Invalid coordinates format! Use 'XX:YY'.")
            return

        # Calculate Euclidean distance between the islands
        distance = math.sqrt((dest_x - start_x) ** 2 + (dest_y - start_y) ** 2) or 0.5  # 0.5 if same island

        # Base speed adjustments
        base_speed = unit_speeds.get(unit_type)

        # Apply Oligarchy bonus (1.10x speed if Oligarchy is active)
        if using_oligarchy:
            base_speed *= 1.1

        # Apply Sea Chart Archive bonus (only for ships, level increases speed)
        if unit_type in ship_units:
            base_speed *= (1 + sea_chart_level / 100)

        # Apply Poseidon Miracle bonus
        if using_poseidon:
            base_speed *= 1.5

        # Time to travel in minutes = 1200 / speed * distance
        travel_time_minutes = (1200 / base_speed) * distance

        # Convert minutes to hours and minutes
        hours = int(travel_time_minutes // 60)
        minutes = int(travel_time_minutes % 60)

        await self.ctx.response.send_message(
            embed=create_embed(
                f"{unit_type.name.replace('_', ' ').title()} from {start_x}:{start_y} to {dest_x}:{dest_y}.",
                f"Travel time is approximately {f'{hours} hours' if hours > 0 else ''}{f' and {minutes} minutes' if minutes > 0 else ''}."
            )
        )
