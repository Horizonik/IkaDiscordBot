import argparse
import os

from commands.list_best_islands import assign_rank_tiers
from utils.constants import ISLAND_RANKINGS_FILE_DIR
from utils.data_utils import fetch_islands_data, save_islands_data_to_file
from utils.general_utils import rank_islands
from utils.settings_manager import get_region_id, get_world_id, REGION_MAPPINGS, WORLD_MAPPINGS


def fetch_rank_all_islands_and_save_to_file(_world_id: int, _region_id: int):
    """
    This function fetches all islands from the world map, ranks them and saves the data into a file.
    It runs periodically to keep the data updated and should never be allowed to be called by a user!
    """

    islands_data = fetch_islands_data(_world_id, _region_id)
    print(f"Fetched {len(islands_data)} islands!")

    ranked_islands = rank_islands(islands_data)
    print(f"Ranked {len(ranked_islands)} islands!")

    tier_ranked_islands = assign_rank_tiers(ranked_islands)
    print(f"Added tiers to {len(tier_ranked_islands)} ranked islands!")

    # Export the ranked islands to a file
    save_islands_data_to_file(tier_ranked_islands, os.path.join(ISLAND_RANKINGS_FILE_DIR, f"{_region_id}_{_world_id}.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and rank islands data.")
    parser.add_argument("world", type=str, help="The name of the world.")
    parser.add_argument("region", type=str, help="The abbreviation of the region.")

    args = parser.parse_args()

    print(f"Running island collection for {args.region} {args.world}")

    # Fetch corresponding region and world IDs
    region_id = get_region_id(args.region, REGION_MAPPINGS)
    world_id = get_world_id(args.world, WORLD_MAPPINGS)

    fetch_rank_all_islands_and_save_to_file(world_id, region_id)
