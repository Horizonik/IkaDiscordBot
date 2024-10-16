from embeds.embeds import travel_time_embed
from utils.constants import ship_units, unit_speeds
from utils.math_utils import get_distance_from_target
from utils.types import BaseCommand


class CalculateTravelTime(BaseCommand):

    async def command_logic(self):
        unit_type = self.command_params.get('unit_type')

        # Validate and parse start coordinates
        try:
            start_x, start_y = map(int, self.command_params['start_coords'].split(':'))
            dest_x, dest_y = map(int, self.command_params['destination_coords'].split(':'))
        except ValueError:
            raise ValueError("invalid coordinates format! Use 'XX:YY'.")

        # Calculate Euclidean distance between the islands
        distance = get_distance_from_target((start_x, start_y), (dest_x, dest_y))
        base_speed, hours, minutes = self.calculate_travel_time(distance, unit_type)

        await self.ctx.response.send_message(
            embed=travel_time_embed(
                unit_type=unit_type,
                start_coords=(start_x, start_y),
                dest_coords=(dest_x, dest_y),
                distance=distance,
                base_speed=base_speed,
                hours=hours,
                minutes=minutes
            )
        )

    def calculate_travel_time(self, distance: float, unit_type: str) -> tuple:
        """Calculates the travel time for a unit to reach a destination"""

        # Get command parameters
        using_poseidon = self.command_params.get('using_poseidon', False)
        using_oligarchy = self.command_params.get('using_oligarchy', False)
        sea_chart_level = self.command_params.get('sea_chart_level', 0)

        base_speed = unit_speeds.get(unit_type)

        # Apply Oligarchy bonus (1.10x speed if Oligarchy is active)
        if using_oligarchy:
            base_speed *= 1.1

        # Apply Sea Chart Archive bonus (only for ships, level increases speed)
        if unit_type in ship_units:
            base_speed *= (1 + sea_chart_level / 100)

        # Apply Poseidon Miracle bonus
        if using_poseidon:
            base_speed *= 2

        # Time to travel in minutes = 1200 / speed * distance
        travel_time_minutes = (1200 / base_speed) * distance

        # Convert minutes to hours and minutes
        hours = int(travel_time_minutes // 60)
        minutes = int(travel_time_minutes % 60)

        return base_speed, hours, minutes
