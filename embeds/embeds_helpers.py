import discord
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

from utils.general_utils import truncate_string
from utils.math_utils import get_distance_from_target
from utils.types import CityData


def create_embed(title: str = "", description: str = "", color: discord.Color = discord.Color.blue(), fields: list = None, footer: tuple = None) -> discord.Embed:
    """Standardize all embeds"""

    if fields is None:
        fields = []

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="© IkaDiscordBot")

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    if footer:
        embed.set_footer(text=footer[0], icon_url=footer[1])

    return embed


def city_to_ascii_table_row(city: CityData, target_coords) -> list[str]:
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


def get_island_residents_info_embed(island_cities_data: list[CityData]) -> tuple[str, str]:
    player_count = {}
    alliance_count = {}

    # Gather player and alliance data
    for city in island_cities_data:
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
