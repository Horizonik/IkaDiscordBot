import math


def get_distance_from_target(city_coords: tuple, target_coords: tuple):
    """Calculates which city is the closest to the target location using the euclidean distance formula"""
    x1, y1 = city_coords
    x2, y2 = target_coords

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
