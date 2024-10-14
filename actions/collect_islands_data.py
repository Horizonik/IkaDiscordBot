# import argparse
#
# from commands.list_best_islands import assign_rank_tiers
# from database.guild_settings_manager import get_value_from_mappings, REGION_MAPPINGS, WORLD_MAPPINGS
# from utils.general_utils import rank_islands
#
#
# def fetch_rank_all_islands_and_save_to_file(_world_id: int, _region_id: int):
#     """
#     This function fetches all islands from the world map, ranks them and saves the data into a file.
#     It runs periodically to keep the data updated and should never be allowed to be called by a user!
#     """
#
#     islands_data = fetch_islands_data(_world_id, _region_id)
#     ranked_islands = rank_islands(islands_data)
#     tier_ranked_islands = assign_rank_tiers(ranked_islands)
#
#     # Export the ranked islands to a file
#     # TODO save island data in db
#
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Fetch and rank islands data.")
#     parser.add_argument("world", type=str, help="The name of the world.")
#     parser.add_argument("region", type=str, help="The abbreviation of the region.")
#
#     args = parser.parse_args()
#
#     print(f"Running island collection for {args.region} {args.world}")
#
#     # Fetch corresponding region and world IDs
#     region_id = get_value_from_mappings(args.region, REGION_MAPPINGS)
#     world_id = get_value_from_mappings(args.world, WORLD_MAPPINGS)
#
#     fetch_rank_all_islands_and_save_to_file(world_id, region_id)
