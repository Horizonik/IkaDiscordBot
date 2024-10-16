import discord
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

from database.guild_settings_manager import get_islands_data
from embeds_helpers import create_embed, city_to_ascii_table_row, get_island_residents_info_embed
from utils.general_utils import truncate_string, get_island_tier, coords_to_string, collect_island_data, calculate_amount_of_open_spots
from utils.types import CityData, UnitType


def calculate_clusters_embed(clusters_as_str: list[str], alliance_name: str) -> discord.Embed:
    fields = []
    for cluster in clusters_as_str:
        cluster_lines = cluster.split('\n')
        header = cluster_lines[0]
        description = '\n'.join(cluster_lines[1:])

        fields.append((header, description, False))

    return create_embed(
        title=f"Cluster Information for alliance {alliance_name.capitalize()}",
        color=discord.Color.blue(),
        fields=fields
    )


def closest_player_city_to_target_embed(closest_city: CityData, target_coords: tuple) -> discord.Embed:
    """Generate embed for closest city result."""

    # Create table with table2ascii
    table_content = t2a(
        header=["Coords", "City Name", "Owner", "Distance"],
        body=[city_to_ascii_table_row(closest_city, target_coords)],
        style=PresetStyle.thick_compact,
        alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER]
    )

    return create_embed(
        description=f"Found the closest city to **{target_coords}**",
        fields=[
            ("", f"```\n{table_content}\n```", False)
        ]
    )


def closest_alliance_member_to_target_embed(closest_cities: list[CityData], target_coords: tuple, alliance_name: str) -> discord.Embed:
    """Generate embed for closest cities in an alliance."""

    # Prepare data for the table
    table_data = []

    for city in closest_cities:
        table_data.append(city_to_ascii_table_row(city, target_coords))

    # Create table with table2ascii
    table_content = t2a(
        header=["Coords", "City Name", "Owner", "Distance"],
        body=table_data,
        style=PresetStyle.thick_compact,
        alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER]
    )

    # Add the table content to the embed
    return create_embed(
        description=f"Found the closest cities in alliance **{alliance_name.capitalize()}** to **{target_coords}**",
        fields=[
            ("", f"```\n{table_content}\n```", False)
        ]
    )


def find_island_embed(island_cities_data: list[CityData], world_id: int, region_id: int) -> discord.Embed:
    island_rankings = get_islands_data(world_id, region_id)
    player_info, alliance_info = get_island_residents_info_embed(island_cities_data)

    island_data = island_cities_data[0].__dict__
    island_data['tier'] = get_island_tier(island_data['x'], island_data['y'], island_rankings)

    table_content = t2a(
        header=["Coords", "Spots", "Wood", "Resource", "Wonder", "Tier"],
        body=[collect_island_data(island_data, coords_to_string((island_data['x'], island_data['y'])))],
        style=PresetStyle.thick_compact,
        alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER]
    )

    # Create embed for island stats
    return create_embed(
        title=f"Stats for island {coords_to_string(island_data['coords'])} {island_data['island_name']}",
        description=(
            f"A beautiful {str(island_data['resource_type'])} {str(island_data['wonder_type'])} island "
            f"with {calculate_amount_of_open_spots(island_data.__dict__)} open spots."
        ),
        fields=[
            ("Island Information", f"```\n{table_content}\n```", False),
            ("Island Residents", f"```\n{player_info}\n```", False),
            ("Alliance Presence", f"```\n{alliance_info}\n```", False)
        ]
    )


def show_settings_embed(settings: dict) -> discord.Embed:
    return create_embed(
        title="Server Settings", description="Current server settings for the bot.",
        fields=[(key.capitalize(), value, False) for key, value in settings.items() if not key.endswith('_id')]
    )


def find_player_embed(cities_data: list[CityData], player_name: str, world_id: int, region_id: int) -> discord.Embed:
    # Load island tier data from the JSON file
    islands_data = get_islands_data(world_id, region_id)

    # Prepare data for the table
    table_data = []
    for city in cities_data:
        # Truncate string that might exceed the embed length limit
        city_name = truncate_string(city.city_name, 7)
        wonder_type = truncate_string(city.wonder_type, 6)
        resource_type = truncate_string(city.resource_type, 6)

        # Get the tier of the island
        island_tier = get_island_tier(city.x, city.y, islands_data)

        # Append row data
        table_data.append([
            f"{city.x}:{city.y}",  # Convert tuple to string
            f"[{city.city_level}]{city_name}",
            f"[{city.resource_level}]{resource_type.capitalize()}",
            f"[{city.wonder_level}]{wonder_type.capitalize()}",
            island_tier  # Add island tier to the table
        ])

    # Create table with table2ascii
    table_content = t2a(
        header=["Coords", "City Name", "Resource", "Miracle", "Tier"],
        body=table_data,
        style=PresetStyle.thick_compact,
        alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER]
    )

    return create_embed(
        title=f"{player_name.capitalize()}'s City Information",
        fields=[
            (f"{len(cities_data)} cities found", f"```\n{table_content}\n```", False)
        ])


def help_embed(ctx: discord.Interaction) -> discord.Embed:
    return create_embed(
        "Help Menu",
        "Here are all the commands available to you.",
        fields=[(f"`/{command.name}`", command.description.capitalize(), False) for command in ctx.client.tree.get_commands()]
    )


def list_best_islands_embed(islands_data: list[tuple[dict, int]], command_params: dict) -> discord.Embed:
    best_islands = islands_data[:10]  # Get the top 10 islands

    # Prepare data for the table
    table_data = []
    for island_data, _ in best_islands:
        table_data.append(collect_island_data(island_data, coords_to_string((island_data['x'], island_data['y']))))

    table_content = t2a(
        header=["Coords", "Spots", "Wood", "Resource", "Wonder", "Tier"],
        body=table_data,
        style=PresetStyle.thick_compact,
        alignments=[Alignment.CENTER, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER]
    )

    # Create embed for island stats
    return create_embed(
        title=f"Top {len(best_islands)} {str(command_params['resource_type'])} {str(command_params['miracle_type'])} islands (Out of {len(islands_data)} applicable)",
        description=f"Top {len(best_islands)} best {str(command_params['resource_type'])} {str(command_params['miracle_type'])} islands",
        fields=[
            ("", f"```\n{table_content}\n```", False)
        ]
    )


def travel_time_embed(unit_type: UnitType, start_coords: tuple, dest_coords: tuple, hours: int, minutes: int, base_speed: int, distance: float) -> discord.Embed:
    description = "Travel time is approximately "
    description += f"{hours} hours" if hours > 0 else ""
    description += " and" if hours > 0 and minutes > 0 else ""
    description += f" {minutes} minutes" if minutes > 0 else ""

    return create_embed(
        f"{unit_type.name.replace('_', ' ').title()} from {':'.join(start_coords)} to {':'.join(dest_coords)}.",
        description=description,
        fields=[
            ("Unit Type", unit_type.name.replace('_', ' ').title(), True),
            ("Base Speed", base_speed, True),
            ("Distance", distance, True),
            ("Travel Time", f"{hours} hours and {minutes} minutes", True),
        ]
    )
