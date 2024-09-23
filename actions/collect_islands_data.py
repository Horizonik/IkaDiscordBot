from commands.list_best_islands import assign_rank_tiers
from utils.constants import ISLAND_RANKINGS_FILE_LOCATION
from utils.data_utils import fetch_islands_data, save_islands_data_to_file
from utils.general_utils import rank_islands


def fetch_rank_all_islands_and_save_to_file():
    """
    This function fetches all islands from the world map, ranks them and saves the data into a file
    It runs periodically to keep the data updated and should never be allowed to be called by a user!
    """
    islands_data = fetch_islands_data()
    print(f"Fetched {len(islands_data)} islands!")
    ranked_islands = rank_islands(islands_data)
    print(f"Ranked {len(ranked_islands)} islands!")
    tier_ranked_islands = assign_rank_tiers(ranked_islands)  # Assign letter-based rankings (S,A,B,C,D tiers)
    print(f"Added tiers to {len(tier_ranked_islands)} ranked islands!")

    # Export the ranked islands to a file
    save_islands_data_to_file(tier_ranked_islands, ISLAND_RANKINGS_FILE_LOCATION)


if __name__ == "__main__":
    fetch_rank_all_islands_and_save_to_file()
