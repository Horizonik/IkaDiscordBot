import copy
import math
import os
import random
from collections import defaultdict
from typing import Any, Optional
import discord
import requests

from .constants import GOOD_WONDERS, BASE_DIR
from .types import CityInfo, IslandInfo, ClusterInfo, ResourceTypes, WonderTypes
import json

# Configuration
DATA_FOLDER = '../data/'
DATA_FETCH_BASE_URL = 'https://ikalogs.ru/common/report/index/'


def load_json_from_file(file_location: str) -> Any:
    if not os.path.exists(file_location):
        raise FileNotFoundError(f"{file_location} not found.")

    with open(file_location, 'r') as file:
        config = json.load(file)

    return config


def validate_alliance_name(alliance_name: str):
    if not alliance_name:
        raise ValueError("Alliance name not found in config.")


def fetch_cities_data(query: str) -> list[CityInfo]:
    """Fetch data from the Ika-logs site"""

    params = {
        'report': "User_WorldFind",
        'query': f"server=2&world=57&{query}&limit=5000",
        'order': "asc",
        "sort": "nick",
        "start": "0",
        "limit": "5000"
    }

    response = requests.post(DATA_FETCH_BASE_URL, params=params)
    if response.headers.get('Content-Type') == 'application/json':
        data: list[dict] = response.json()['body']['rows']
        return [CityInfo(row) for row in data]
    else:
        raise ValueError("Error! Page did not return any JSON data!")


def convert_data_to_markdown(parsed_city_clusters: list[ClusterInfo]) -> str:
    data_as_markdown = "# City Clusters:\n"

    for cluster in parsed_city_clusters:
        data_as_markdown += f"{cluster}\n\n"

    return data_as_markdown


def filter_data_by_min_amount_of_cities_on_island(
        cities_data: list[CityInfo],
        city_counts: dict,
        min_cities_on_island: int = 0
) -> list[CityInfo]:
    return [city for city in cities_data if city_counts[city.coords] >= min_cities_on_island]


def count_cities_per_island(cities_data: list[CityInfo]) -> dict:
    city_counts = defaultdict(int)

    for city in cities_data:
        # Use the coords attribute instead of x and y
        city_counts[city.coords] += 1

    return dict(city_counts)


def convert_data_to_embed(parsed_city_clusters: list[ClusterInfo]) -> discord.Embed:
    embed = discord.Embed(title="City Clusters", color=discord.Color.blue())

    for cluster in parsed_city_clusters:
        cluster_total_cities = len(cluster.cities)
        cluster_details = []

        # Group the cities by island and count how many cities each island has
        islands_dict = {}
        for city in cluster.cities:
            if city.coords not in islands_dict:
                islands_dict[city.coords] = {
                    "city_count": 0,
                    "owners": set()
                }
            islands_dict[city.coords]["city_count"] += 1
            islands_dict[city.coords]["owners"].add(city.player_name)

        # Build the text structure for each island in this cluster
        for coords, details in islands_dict.items():
            owners_str = ', '.join(details["owners"])
            city_str = f"- {coords} -> {details['city_count']} cities ({owners_str})"
            cluster_details.append(city_str)

        # Join all islands' details into a single text block
        cluster_text = '\n'.join(cluster_details)

        # Add the field for this cluster
        embed.add_field(
            name=f"City Cluster {cluster.name} - total of {cluster_total_cities}",
            value=cluster_text,
            inline=False
        )

    return embed


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


def get_distance_from_target(city_coords: tuple, target_coords: tuple):
    """Calculates which city is the closest to the target location using the euclidean distance formula"""
    x1, y1 = city_coords
    x2, y2 = target_coords

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def save_islands_data_to_file(islands_data: list[IslandInfo], filename: str = "islands_data.json"):
    # Convert IslandInfo objects into dictionaries for JSON serialization
    for island in islands_data:
        try:
            island.cities = [city.__dict__ for city in island.cities]
        except AttributeError as e:
            print(f"Error processing island {island.name} {island.coords}: {e}")
            island.cities = []  # Handle the error by resetting or logging

    data = [island.__dict__ for island in islands_data]
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def load_islands_data_from_file(filename: str = "islands_data.json") -> Optional[list[IslandInfo]]:
    try:
        with open(filename, 'r') as file:
            data = json.load(file)

        # Convert dictionaries back into IslandInfo objects
        islands = []
        for island_data in data:
            # Assuming the city data needs to be converted back to CityInfo objects
            cities = [CityInfo(city_data) for city_data in island_data.pop('cities', [])]
            island = IslandInfo(island_data, cities)
            islands.append(island)

        return islands
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return None


def create_island_info(cities: list[CityInfo]) -> IslandInfo:
    """
    Create a new IslandInfo object from a list of CityInfo objects.
    Assumes that all cities belong to the same island.

    Args:
        cities (list[CityInfo]): A list of CityInfo objects representing cities on the island.

    Returns:
        IslandInfo: A new IslandInfo object with data aggregated from the cities.
    """

    city_as_dict = cities[0].__dict__  # Grab a single city to extract data about the island from it
    return IslandInfo(city_as_dict, cities)


def fetch_islands_data() -> list[IslandInfo]:
    """Fetches every island's data from across the map and saves it into a file"""
    islands_data = []

    for x_coords in range(20, 80):
        for y_coords in range(20, 80):
            cities_data = fetch_cities_data(f"state=&search=city&x={x_coords}&y={y_coords}")
            if cities_data:
                island_data = create_island_info(cities_data)
                print(f"Fetched {len(island_data.cities)} cities for island {island_data.name} {island_data.coords}.")
                islands_data.append(island_data)
            else:
                print(f"The island ({x_coords}, {y_coords}) has 0 residents. Continuing..")

        # Save existing data after finishing each x_coord
        if islands_data:
            save_islands_data_to_file(copy.deepcopy(islands_data), os.path.join(BASE_DIR, 'data', f'backup_data_for_x_iter_{x_coords}.json'))
            print(f">> Saved the data we collected up to now in a file called backup_data_for_x_iter_{x_coords}")

    return islands_data


def rank_islands(islands_data: list[IslandInfo], resource_type: ResourceTypes = None, miracle_type: WonderTypes = None, no_full_islands: bool = False) -> list[tuple[IslandInfo, int]]:
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
    ranked_islands.sort(key=lambda ranked_island: ranked_island[1], reverse=True)  # ranked_island[1] is the score of the island

    return ranked_islands


def truncate_string(raw_string: str, char_limit: int):
    return raw_string if len(raw_string) <= char_limit else raw_string[:char_limit - 2] + '..'
