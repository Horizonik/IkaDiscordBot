from table2ascii import table2ascii as t2a, PresetStyle, Alignment
import discord

from utils.constants import ISLAND_RANKINGS_FILE_LOCATION
from utils.types import BaseCommand, IslandInfo
from utils.utils import load_islands_data_from_file, rank_islands, truncate_string


class ListBestIslands(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)

    async def command_logic(self):
        ranked_islands_data = load_islands_data_from_file(ISLAND_RANKINGS_FILE_LOCATION)
        if not ranked_islands_data:
            raise ValueError("the island rankings db is empty, please try again later. If this issue persists please contact my creator.")

        ranked_islands = rank_islands(ranked_islands_data, self.command_params['resource_type'], self.command_params['miracle_type'], self.command_params['no_full_islands'])

        embed = self.create_island_ranking_embed(ranked_islands)
        await self.ctx.response.send_message(embed=embed)

    def create_island_ranking_embed(self, islands_data: list[tuple[IslandInfo, int]]) -> discord.Embed:
        """Generates a table that shows the best islands and their ranking"""
        best_islands = islands_data[:10]  # Get the top 10 islands

        embed = discord.Embed(
            title=f"Top {len(best_islands)} out of {len(islands_data)} islands",
            description=f"All islands have the {str(self.command_params['miracle_type']).capitalize()} miracle and {str(self.command_params['resource_type']).capitalize()} resource.",
            color=discord.Color.blue()
        )

        # Prepare data for the table
        table_data = []
        for island, _ in best_islands:
            coords = f"{island.coords[0]}:{island.coords[1]}"
            open_slots = 16 - len(island.cities) if hasattr(island, 'cities') else 16
            wood_level = island.wood_level
            wonder_info = f"[{island.wonder_level}]{truncate_string(island.wonder_type, 6).capitalize()}"
            resource_info = f"[{island.resource_level}]{truncate_string(island.resource_type, 6).capitalize()}"
            tier = island.tier

            # Append row data
            table_data.append([coords, open_slots, wood_level, resource_info, wonder_info, tier])

        # Create table with table2ascii
        table_content = t2a(
            header=["Coords", "Spots", "Wood", "Resource", "Wonder", "Tier"],
            body=table_data,
            style=PresetStyle.thick_compact,
            alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER]
        )

        # Add the table content to the embed
        embed.add_field(name="", value=f"```\n{table_content}\n```", inline=False)

        # Footer and additional info
        embed.set_footer(text="Rankings are based on mine levels, wonders, available spots and distance from center of the map.")

        return embed


def assign_rank_tiers(ranked_islands: list[tuple[IslandInfo, int]]) -> list[IslandInfo]:
    # Extract scores and calculate min and max
    scores = [score for _, score in ranked_islands]
    max_score = max(scores)
    min_score = min(scores)

    # Define thresholds for letter-based ranking
    def get_letter_rank(score: int) -> str:
        score_range = max_score - min_score
        if score >= min_score + 0.8 * score_range:
            return 'S'
        elif score >= min_score + 0.6 * score_range:
            return 'A'
        elif score >= min_score + 0.4 * score_range:
            return 'B'
        elif score >= min_score + 0.2 * score_range:
            return 'C'
        else:
            return 'D'

    # Assign letter rankings based on score
    for island, score in ranked_islands:
        island.tier = get_letter_rank(score)

    # Discard the scores now that each island has a tier
    return [island for island, score in ranked_islands]
