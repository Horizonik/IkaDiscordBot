import json
import os

import discord
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

from utils.constants import ISLAND_RANKINGS_FILE_DIR
from utils.data_utils import fetch_data
from utils.general_utils import create_embed, calculate_amount_of_open_spots, get_island_tier, collect_island_data, coords_to_string
from utils.types import BaseCommand, IslandData


class FindIsland(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict, server_settings: dict):
        super().__init__(ctx, params, server_settings)

    async def command_logic(self):
        """
        Handles the core logic for the find island command.

        Raises:
            ValueError: If the coordinates provided are in an invalid format.
            ValueError: If no cities are found on the island at the specified coordinates.

        Fetches data based on the provided coordinates, converts the data to an `IslandData`
        object and sends the result as an embed message.

        Returns:
            None
        """
        # Validate that the coords are in format xx:yy
        try:
            x, y = map(int, self.command_params.get('coords').split(':'))
        except ValueError:
            raise ValueError(f"Invalid coordinates format: {self.command_params.get('coords')}. Expected format 'X:Y'.")

        # Fetch the data of the cities present on the selected island
        island_cities_data = fetch_data(f"server={self.region_id}&world={self.world_id}&search=city&x={x}&y={y}")

        if not island_cities_data:
            raise ValueError(f"could not find any cities on the island at {x}:{y}!")

        # Convert island_data from dict to IslandData object
        island_cities_data = IslandData(island_cities_data[0].__dict__, island_cities_data)

        embed = self.get_result_as_embed(island_cities_data)

        # noinspection PyUnresolvedReferences
        await self.ctx.response.send_message(embed=embed)

    @staticmethod
    def load_island_tiers(filepath: str):
        """Loads island tier data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError as e:
            print(f"Did not find islands data file! Error: {e}")
            return {}

    def collect_player_data(self, island_data: IslandData) -> tuple[str, str]:
        player_count = {}
        alliance_count = {}

        # Gather player and alliance data
        for city in island_data.cities:
            player_count[city.player_name] = player_count.get(city.player_name, 0) + 1
            if city.ally_name:
                alliance_count[city.ally_name] = alliance_count.get(city.ally_name, 0) + 1

        # Sort player data by number of cities (descending)
        sorted_players = sorted(player_count.items(), key=lambda x: x[1], reverse=True)

        # Format player information using t2a
        player_table = t2a(
            header=["Player", "Cities"],
            body=[[player, f"{count} {'cities' if count > 1 else 'city'}"] for player, count in sorted_players],
            style=PresetStyle.thick_compact,
            alignments=[Alignment.LEFT, Alignment.RIGHT]
        )

        # Sort alliance data by number of players (descending)
        if alliance_count:
            sorted_alliances = sorted(alliance_count.items(), key=lambda x: x[1], reverse=True)
            alliance_table = t2a(
                header=["Alliance", "Players"],
                body=[[ally, f"{count} {'players' if count > 1 else 'player'}"] for ally, count in sorted_alliances],
                style=PresetStyle.thick_compact,
                alignments=[Alignment.LEFT, Alignment.RIGHT]
            )
        else:
            alliance_table = "No alliances on this island."

        return player_table or "No players on this island.", alliance_table

    def get_result_as_embed(self, island_data: IslandData) -> discord.Embed:
        # Load island tier data from the JSON file
        island_rankings = self.load_island_tiers(os.path.join(ISLAND_RANKINGS_FILE_DIR, f'{str(self.region_id)}_{str(self.world_id)}.json'))
        island_data.tier = get_island_tier(island_data.coords, island_rankings)

        # Collect island data
        table_content = collect_island_data(island_data, coords_to_string(island_data.coords))

        table_content = t2a(
            header=["Coords", "Spots", "Wood", "Resource", "Wonder", "Tier"],
            body=[table_content],
            style=PresetStyle.thick_compact,
            alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER]
        )

        # Create embed for island stats
        embed = create_embed(
            title=f"Stats for island {coords_to_string(island_data.coords)} {island_data.name}",
            description=(
                f"A beautiful {str(island_data.resource_type)} {str(island_data.wonder_type)} island "
                f"with {calculate_amount_of_open_spots(island_data)} open spots."
            )
        )
        embed.add_field(name="Island Information", value=f"```\n{table_content}\n```", inline=False)

        # Collect player and alliance data
        player_info, alliance_info = self.collect_player_data(island_data)

        # Add player info to the embed
        embed.add_field(name="Island Residents", value=f"```\n{player_info}\n```", inline=False)

        # Add alliance info if there are alliances
        if alliance_info:
            embed.add_field(name="Alliance Presence", value=f"```\n{alliance_info}\n```", inline=False)

        return embed
