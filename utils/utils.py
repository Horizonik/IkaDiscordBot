import json
import os
import random
from collections import defaultdict
from typing import Any
import discord
import requests
from .types import CityInfo, IslandInfo, ClusterInfo

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


def fetch_data(query: str) -> list[CityInfo]:
    """Fetch data from the ikalogs site"""

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

# 'https://ikalogs.ru/common/report/index/?report=User_WorldFind&query=server%3D2%26world%3D57%26state%3D%26search%3Dcity%26nick%3DGemmy%26ally%3DNone%26limit%3D5000&order=asc&sort=nick&start=0&limit=5000'

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


def get_islands_info(cities_data: list[CityInfo]) -> list[IslandInfo]:
    """Goes over the scraped cities' data, extracts information relating to the island"""

    island_info_dict = {}

    for city in cities_data:
        island_coords = city.coords  # Using coords from CityInfo
        if island_coords not in island_info_dict:
            # Initialize a new IslandInfo entry if it doesn't exist
            island_info_dict[island_coords] = {
                'resource_type': city.tradegood_type,
                'resource_level': city.island_tradegood,
                'wood_level': city.island_wood,
                'wonder_level': city.island_wonder,
                'x': island_coords[0],
                'y': island_coords[1],
                'coords': city.coords,
            }

    # Create IslandInfo instances from the dictionary
    island_info_list = [
        IslandInfo(data) for data in island_info_dict.values()
    ]

    return island_info_list


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
    ]
    suffixes = [
        "os", "a", "on", "us", "ia", "ion", "e", "aia", "ikos", "opolis",
    ]

    return f"{random.choice(prefixes)}{random.choice(suffixes)}"
