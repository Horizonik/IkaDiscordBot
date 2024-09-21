import math
import discord
from utils.types import BaseCommand


class CalculateTravelTime(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)
        self.command_params = params

    async def command_logic(self):
        unit_type = self.command_params['unit_type']
        using_poseidon = self.command_params['using_poseidon']

        # Validate and parse start coordinates
        try:
            start_x, start_y = map(int, self.command_params['start_coords'].split(':'))
            dest_x, dest_y = map(int, self.command_params['destination_coords'].split(':'))

        except ValueError:
            await self.ctx.response.send_message("Invalid start coordinates format! Please use 'XX:YY'.")
            return

        start_coords = (start_x, start_y)
        destination_coords = (dest_x, dest_y)

        # Speeds for land and sea units
        speeds = {
            "land": 3,
            "sea": 2
        }

        # Get the speed based on the unit type
        speed = speeds.get(unit_type.lower())
        if speed is None:
            await self.ctx.response.send_message("Invalid unit type! Please use 'land' or 'sea'.")
            return

        # Calculate the distance
        distance = math.sqrt(
            (destination_coords[0] - start_coords[0]) ** 2 +
            (destination_coords[1] - start_coords[1]) ** 2
        )

        # Calculate estimated travel time in hours
        estimated_time_in_hrs = distance / speed
        estimated_time_in_hrs = estimated_time_in_hrs / 2 if using_poseidon else estimated_time_in_hrs

        # Format the result
        hours = int(estimated_time_in_hrs)
        minutes = int((estimated_time_in_hrs - hours) * 60)

        response_message = (
            f"It will take approximately {f'{hours} hours and ' if hours else ''}"
            f"{minutes} minutes for your {unit_type} units to reach from "
            f"{':'.join(map(str, start_coords))} to {':'.join(map(str, destination_coords))}."
        )

        await self.ctx.response.send_message(response_message)
