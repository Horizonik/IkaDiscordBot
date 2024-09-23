import copy
import json
import os
from typing import Optional

import requests

from utils.constants import BASE_DIR, DATA_FETCH_BASE_URL
from utils.types import CityInfo, IslandInfo


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


def fetch_cities_data(query: str, player_name: str = None) -> list[CityInfo]:
    """
    Fetch city data from the Ika-logs site based on the provided query.

    :param query: url params for the api call.
    :param player_name: optional - if provided, will filter the cities to only those owned by the player.
    :return: The cities data in CityInfo object format
    """

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
        cities = [CityInfo(row) for row in data]

        if player_name:
            # Filter out any startsWith matches, only exact name matches will remain
            cities = [city for city in cities if city.player_name.lower() == player_name]

        return cities

    else:
        raise ValueError("Error! Page did not return any JSON data!")
