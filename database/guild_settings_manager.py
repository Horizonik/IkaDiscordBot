import os
import sqlite3

import discord

from utils.constants import BOT_ENV, BASE_DIR
from utils.constants import DEFAULT_SETTINGS_FILE_PATH
from utils.data_utils import load_json_file

SETTINGS_TABLE_NAME = f'{BOT_ENV}_guild_settings'
DEFAULT_SETTINGS = load_json_file(DEFAULT_SETTINGS_FILE_PATH)


def get_value_from_mappings(region_name: str, region_mapping: dict):
    if region_name not in region_mapping:
        raise ValueError(f"Region '{region_name}' is invalid.")

    return region_mapping[region_name]


def get_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'database', 'guild_settings.sqlite'))
    conn.row_factory = sqlite3.Row

    return conn


def get_table(name: str) -> list[dict]:
    """Fetch settings for a specific guild from the database."""

    if not is_table_exist(name):
        raise ValueError(f"Table '{name}' does not exist.")

    return run_query(f"SELECT * FROM {name}")


def is_table_exist(table_name: str) -> bool:
    result = run_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return result is not None


def run_query(query: str) -> list[dict]:
    """Executes a query on the db and returns the results."""
    conn = get_connection()
    cursor = conn.cursor()

    print("Running query:", query)
    cursor.execute(query)

    # Commit the transaction if it modifies the database (e.g., UPDATE, INSERT, DELETE)
    if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
        conn.commit()
        return []

    result = cursor.fetchall()
    conn.close()

    return [dict(row) for row in result]


def get_islands_data(world_id: int, region_id: int) -> list[dict]:
    """Fetch all islands from the world map."""
    # Add subquery for cities_data to get each islands city based on foregin key
    return run_query(f"""
        SELECT * FROM islands_data
        WHERE 
            region_id = {region_id} 
            AND world_id = {world_id}
    """)


def fetch_settings(guild: discord.Guild) -> dict:
    """Fetch settings for a specific guild from the database."""
    results = run_query(f"""SELECT * FROM {SETTINGS_TABLE_NAME} WHERE guild_id = {guild.id}""")
    return results[0] if results else {}


def update_setting(guild: discord.Guild, column_name: str, new_value: str):
    """Update a specific guild setting in the database."""

    # Get world id and region id
    if column_name == 'world':
        value_id = run_query(f"""SELECT * FROM worlds WHERE name = '{new_value}'""")
        if value_id:
            value_id = value_id[0]['id']
        else:
            raise ValueError(f"World '{new_value}' is invalid.")

    elif column_name == 'region':
        value_id = run_query(f"""SELECT * FROM regions WHERE short_name = '{new_value}' OR name = '{new_value}'""")
        if value_id:
            value_id = value_id[0]['id']
        else:
            raise ValueError(f"Region '{new_value}' is invalid.")

    else:
        raise ValueError("Invalid setting name. Allowed columns are: 'world', 'region'.")

    run_query(f"""
        UPDATE {SETTINGS_TABLE_NAME}
        SET {column_name} = '{new_value}',
            {column_name}_id = {value_id}
        WHERE guild_id = {guild.id}
    """)


def save_settings(guild: discord.Guild, world, region, world_id, region_id):
    """Save or update guild settings in the database."""

    run_query(f"""
        INSERT INTO {SETTINGS_TABLE_NAME} (guild_id, guild_name, world, region, world_id, region_id)
        VALUES ({guild.id}, '{guild.name}', '{world}', '{region}', {world_id}, {region_id})
        
        ON CONFLICT(guild_id) DO UPDATE SET
            guild_name = excluded.guild_name,
            world = excluded.world,
            region = excluded.region,
            world_id = excluded.world_id,
            region_id = excluded.region_id;
    """)


def fetch_or_create_settings(guild: discord.Guild) -> dict:
    settings = fetch_settings(guild)

    if not settings:
        # Initialize guild settings if missing
        save_settings(guild, **DEFAULT_SETTINGS)
        settings = fetch_settings(guild)

    return settings


REGION_MAPPINGS = get_table('regions')
WORLD_MAPPINGS = get_table('worlds')
