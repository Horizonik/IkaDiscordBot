# Helper functions for ID conversions
import json

from utils.constants import DEFAULT_SETTINGS_FILE_PATH, REGION_MAPPINGS_FILE_PATH, WORLD_MAPPINGS_FILE_PATH
from utils.data_utils import load_json_file

REGION_MAPPINGS = load_json_file(REGION_MAPPINGS_FILE_PATH)
WORLD_MAPPINGS = load_json_file(WORLD_MAPPINGS_FILE_PATH)


def load_settings_with_ids(settings_file: str, region_mapping: dict, world_mapping: dict) -> dict:
    settings = load_json_file(settings_file)

    for guild_id, guild_settings in settings.items():
        # Convert region names to IDs
        if 'region' in guild_settings:
            region_name = guild_settings['region']
            guild_settings['region_id'] = get_region_id(region_name, region_mapping)

        # Convert world titles to IDs
        if 'world' in guild_settings:
            world_title = guild_settings['world']
            guild_settings['world_id'] = get_world_id(world_title, world_mapping)

    return settings


def save_settings(settings, settings_file_path: str):
    with open(settings_file_path, 'w') as f:
        json.dump(settings, f, indent=4)


def get_region_id(region_name: str, region_mapping: dict):
    if region_name not in region_mapping:
        raise ValueError(f"Region '{region_name}' is invalid.")
    return region_mapping[region_name]


def get_world_id(world_title: str, world_mapping: dict):
    if world_title not in world_mapping:
        raise ValueError(f"World '{world_title}' is invalid.")
    return world_mapping[world_title]


def validate_server_settings(server_settings: dict, default_settings: dict) -> dict:
    """Ensure server settings exist and validate necessary fields."""
    for guild_id in server_settings.keys():

        # Ensure guild has both settings
        if 'region' not in server_settings[guild_id]:
            server_settings[guild_id]['region'] = default_settings['region']

        if 'world' not in server_settings[guild_id]:
            server_settings[guild_id]['world'] = default_settings['world']

        # Ensure corresponding IDs exist
        if 'region_id' not in server_settings[guild_id] or server_settings[guild_id]['region_id'] is None:
            server_settings[guild_id]['region_id'] = get_region_id(server_settings[guild_id]['region'], REGION_MAPPINGS)

        if 'world_id' not in server_settings[guild_id] or server_settings[guild_id]['world_id'] is None:
            server_settings[guild_id]['world_id'] = get_world_id(server_settings[guild_id]['world'], WORLD_MAPPINGS)

    return server_settings


# Fetched data
DEFAULT_SETTINGS = load_json_file(DEFAULT_SETTINGS_FILE_PATH)
