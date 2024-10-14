import random
from collections import defaultdict

import discord

from utils.constants import GOOD_WONDERS
from utils.math_utils import get_distance_from_target
from utils.types import CityData, ResourceType, WonderType


def count_cities_per_island(cities_data: list[CityData]) -> dict:
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


def rank_islands(islands_data: list[dict], resource_type: ResourceType = None, miracle_type: WonderType = None, no_full_islands: bool = False) -> list[tuple[dict, int]]:
    # Filter islands based on the input criteria

    if resource_type:
        islands_data = [island for island in islands_data if island['resource_type'] == str(resource_type)]

    if miracle_type:
        islands_data = [island for island in islands_data if island['wonder_type'] == str(miracle_type)]

    if no_full_islands:
        # Check how many times an island appears in the list
        islands_data = [island for island in islands_data if island['taken_spots'] < 16]

    # Calculate ranking score for each island
    def calculate_rank(island: dict) -> int:
        rank_score = 0
        free_spots_weight = 5  # Score weight per free spot

        # Prioritize islands with free spots (max 16 cities per island)
        free_spots = 16 - len(island.cities) if hasattr(island, 'cities') else 16
        rank_score += free_spots * free_spots_weight

        # Add wood, resource, and wonder levels to the score
        rank_score += island['wood_level'] * 5
        rank_score += island['resource_level'] * 6
        rank_score += island['wonder_level'] * 2

        # Extra boost if the wonder is considered "good"
        if island['wonder_type'] in map(str, GOOD_WONDERS):
            rank_score += 150

        # Rank the island higher the closer it is to the map's center
        distance_from_center = get_distance_from_target((island['x'], island['y']), (50, 50))
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
    embed.set_footer(text="© IkaDiscordBot, by Gemesil")

    return embed


def calculate_amount_of_open_spots(island_data: dict) -> int:
    return 16 - island_data['taken_spots']


def get_island_tier(x_pos: int, y_pos: int, islands_data: list[dict]) -> str:
    if not islands_data:
        return 'N/A'

    for island in islands_data:
        if 'tier' in island:
            if island['x'] == x_pos and island['y'] == y_pos:
                return island['tier']
        else:
            return 'N/A'


def collect_island_data(island_data: dict, coords: tuple) -> list[tuple | int | str]:
    # Format island information
    open_spots = calculate_amount_of_open_spots(island_data)
    wonder_info = f"[{island_data['wonder_level']}]{truncate_string(island_data['wonder_type'], 6).capitalize()}"
    resource_info = f"[{island_data['resource_level']}]{truncate_string(island_data['resource_type'], 6).capitalize()}"

    # Append row data for the table
    return [coords, open_spots, island_data['wood_level'], resource_info, wonder_info, island_data['tier']]


def coords_to_string(coords: tuple):
    return f"{coords[0]}:{coords[1]}"


def str_and_lower(raw_string: any) -> str:
    return str(raw_string).lower()
