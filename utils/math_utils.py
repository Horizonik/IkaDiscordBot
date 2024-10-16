import math

from utils.types import CityData


def get_distance_from_target(city_coords: tuple, target_coords: tuple):
    """Calculates which city is the closest to the target location using the Euclidean distance formula"""
    x1, y1 = city_coords
    x2, y2 = target_coords

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) or 0.5  # 0.5 if same island


def get_closest_city(cities_data: list[CityData], target_coords: tuple) -> CityData:
    """Helper method to find the closest city of a list of cities to the target coordinates"""
    return min(cities_data, key=lambda city: get_distance_from_target(city.coords, target_coords))
