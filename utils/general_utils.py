import random
from collections import defaultdict

import discord

from constants import GOOD_WONDERS
from math_utils import get_distance_from_target
from types import CityInfo, IslandInfo, ResourceType, WonderType


def count_cities_per_island(cities_data: list[CityInfo]) -> dict:
    city_counts = defaultdict(int)

    for city in cities_data:
        # Use the coords attribute instead of x and y
        city_counts[city.coords] += 1

    return dict(city_counts)


def generate_cluster_name() -> str:
    prefixes = [
        "Aeg", "Del", "Ere", "Heli", "Kalo", "Nis", "Olym", "Thal", "Xan", "Zef",
        "Thes", "Elys", "Hel", "Kri", "Phae", "Ly", "Axi", "Nyx", "Zephy", "Chal",
    ]

    suffixes = [
        "os", "a", "on", "us", "ia", "ion", "e", "aia", "ikos", "opolis",
        "is", "ae", "iax", "eia", "icus", "osios", "thys", "umos", "iaxis", "eos",
    ]

    return f"{random.choice(prefixes)}{random.choice(suffixes)}"


def rank_islands(islands_data: list[IslandInfo], resource_type: ResourceType = None, miracle_type: WonderType = None,
                 no_full_islands: bool = False) -> list[tuple[IslandInfo, int]]:
    # Filter islands based on the input criteria
    if resource_type:
        islands_data = [island for island in islands_data if island.resource_type == str(resource_type)]

    if miracle_type:
        islands_data = [island for island in islands_data if island.wonder_type == str(miracle_type)]

    if no_full_islands:
        islands_data = [island for island in islands_data if len(island.cities) < 16]

    # Calculate ranking score for each island
    def calculate_rank(island: IslandInfo) -> int:
        rank_score = 0
        free_spots_weight = 5  # Score weight per free spot

        # Prioritize islands with free spots (max 16 cities per island)
        free_spots = 16 - len(island.cities) if hasattr(island, 'cities') else 16
        rank_score += free_spots * free_spots_weight

        # Add wood, resource, and wonder levels to the score
        rank_score += island.wood_level * 5
        rank_score += island.resource_level * 6
        rank_score += island.wonder_level * 2

        # Extra boost if the wonder is considered "good"
        if island.wonder_type in map(str, GOOD_WONDERS):
            rank_score += 150

        # Rank the island higher the closer it is to the map's center
        distance_from_center = get_distance_from_target(island.coords, (50, 50))
        rank_score -= int(distance_from_center)

        return rank_score

    # List of islands with their rank scores
    ranked_islands = [(island, calculate_rank(island)) for island in islands_data]
    ranked_islands.sort(key=lambda ranked_island: ranked_island[1],
                        reverse=True)  # ranked_island[1] is the score of the island

    return ranked_islands


def truncate_string(raw_string: str, char_limit: int):
    return raw_string if len(raw_string) <= char_limit else raw_string[:char_limit - 2] + '..'


def create_embed(title: str = "", description: str = "", color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Standardize all embeds"""

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=f"© IkaDiscordBot, by Gemesil")

    return embed
