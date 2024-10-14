import discord
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

from database.guild_settings_manager import get_islands_data
from utils.general_utils import rank_islands, create_embed, collect_island_data, coords_to_string
from utils.types import BaseCommand, IslandData


class ListBestIslands(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict, guild_settings: dict):
        super().__init__(ctx, params, guild_settings)

    async def command_logic(self):
        ranked_islands_data = get_islands_data(self.world_id, self.region_id)

        if not ranked_islands_data:
            raise ValueError(
                f"island data is not yet available for the {str(self.guild_settings['region']).upper()} {str(self.guild_settings['world']).capitalize()} server. Sorry")

        ranked_islands = rank_islands(ranked_islands_data, self.command_params['resource_type'], self.command_params['miracle_type'], self.command_params['no_full_islands'])
        embed = self.get_result_as_embed(ranked_islands)
        # noinspection PyUnresolvedReferences
        await self.ctx.response.send_message(embed=embed)

    def get_result_as_embed(self, islands_data: list[tuple[dict, int]]) -> discord.Embed:
        best_islands = islands_data[:10]  # Get the top 10 islands

        # Prepare data for the table
        table_data = []
        for island_data, _ in best_islands:
            table_data.append(collect_island_data(island_data, coords_to_string((island_data['x'], island_data['y']))))

        table_content = t2a(
            header=["Coords", "Spots", "Wood", "Resource", "Wonder", "Tier"],
            body=table_data,
            style=PresetStyle.thick_compact,
            alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER]
        )

        # Create embed for island stats
        embed = create_embed(
            title=f"Top {len(best_islands)} {str(self.command_params['resource_type'])} {str(self.command_params['miracle_type'])} islands (Out of {len(islands_data)} applicable)",
            description=f"Top {len(best_islands)} best {str(self.command_params['resource_type'])} {str(self.command_params['miracle_type'])} islands"
        )

        embed.add_field(name="", value=f"```\n{table_content}\n```", inline=False)

        return embed


def assign_rank_tiers(ranked_islands: list[tuple[IslandData, int]]) -> list[IslandData]:
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
