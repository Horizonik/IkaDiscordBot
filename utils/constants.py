import os

from utils.types import WonderTypes

GOOD_WONDERS = [WonderTypes.POSEIDON, WonderTypes.FORGE]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
ISLAND_RANKINGS_FILE_LOCATION = os.path.join(BASE_DIR, 'data', 'island_rankings.json')

###
# Parameters descriptions for every command. These are imported into bot.py for use with discord.py
###

CALCULATE_CLUSTERS_DESCRIPTION = {
    "alliance_name": "Name of the alliance to calculate clusters for",
    "min_cities_per_island": "Minimum number of cities required on an island for it to be included",
    "max_cluster_distance": "Maximum distance between islands to be considered in the same cluster",
    "min_cities_per_cluster": "Minimum amount of cities required for a cluster to be included"
}

GENERATE_HEATMAP_DESCRIPTION = {
    "alliance_name": "Name of the alliance",
    "min_cities_on_island": "Minimum cities on an island"
}

FIND_PLAYER_DESCRIPTION = {
    "player_name": "The name of the player",
    "alliance_name": "Optional - Name of the alliance the player belongs to"
}

TRAVEL_TIME_DESCRIPTION = {
    "unit_type": "LAND/SEA",
    "start_coords": "The coords that the units come from",
    "destination_coords": "The desired destination for the units",
    "using_poseidon": "Are you using the Poseidon miracle (100% reduction)?"
}

CLOSEST_CITY_TO_TARGET_DESCRIPTION = {
    "player_name": "The name of the player",
    "coords": "The target location to which we will compare city distances of the selected player"
}

LIST_BEST_ISLANDS_DESCRIPTION = {
    "resource_type": "Filter for islands that only contain this specific resource",
    "miracle_type": "Filter for islands that only contain this specific miracle",
    "no_full_islands": "Do you want to see full islands in the results? Default true.",
}
