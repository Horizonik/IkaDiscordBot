import os
import discord
from discord import app_commands
from commands.calculate_clusters import CalculateClusters
from commands.closest_city_to_target import ClosestCityToTarget
from commands.travel_time import CalculateTravelTime
from commands.find_player import FindPlayer
from commands.command_descriptions import (
    CALCULATE_CLUSTERS_DESCRIPTION,
    FIND_PLAYER_DESCRIPTION,
    TRAVEL_TIME_DESCRIPTION, CLOSEST_CITY_TO_TARGET_DESCRIPTION
)
from utils.types import DiscordBotClient

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = DiscordBotClient(intents=intents)
BOT_TOKEN = os.getenv('BOT_TOKEN')


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


async def run_command(interaction, command_class, command_params: dict = None):
    """Dynamically run the logic for a given command and allow sending a response"""
    if command_params is None:
        command_params = {}

    # Create an instance of the command class and run it
    command_class_instance = command_class(interaction, command_params)
    await command_class_instance.run()


###
# COMMANDS
###
@client.tree.command()
@app_commands.describe(**CALCULATE_CLUSTERS_DESCRIPTION)
async def calculate_clusters(interaction: discord.Interaction, alliance_name: str, min_cities_per_island: int, max_cluster_distance: int, min_cities_per_cluster: int):
    """Calculates which island groups have the most cities from the selected alliance"""
    await run_command(interaction, CalculateClusters, {
        'alliance_name': alliance_name,
        'min_cities_per_island': min_cities_per_island,
        'max_cluster_distance': max_cluster_distance,
        'min_cities_per_cluster': min_cities_per_cluster
    })


# TODO - Disabled until further notice. Need to generate the heatmap as an image that can be sent to discord.
# @client.tree.command()
# @app_commands.describe(**GENERATE_HEATMAP_DESCRIPTION)
# async def generate_heatmap(interaction: discord.Interaction, alliance_name: str, min_cities_on_island: int):
#     """Generates a heatmap based on the alliance and minimum cities"""
#     await run_command(interaction, GenerateHeatmap,
#                       {"alliance_name": alliance_name, "min_cities": min_cities_on_island})


@client.tree.command()
@app_commands.describe(**FIND_PLAYER_DESCRIPTION)
async def find_player(interaction: discord.Interaction, player_name: str, alliance_name: str = None):
    """Retrieves information about the player's cities locations"""
    await run_command(interaction, FindPlayer, {"player_name": player_name.lower(), "alliance_name": alliance_name})


@client.tree.command()
@app_commands.describe(**TRAVEL_TIME_DESCRIPTION)
async def travel_time(interaction: discord.Interaction, unit_type: str, start_coords: str, destination_coords: str, using_poseidon: bool = False):
    """Calculates estimated travel time for units based on type and coordinates"""
    await run_command(interaction, CalculateTravelTime, {
        "unit_type": unit_type,
        "start_coords": start_coords,
        "destination_coords": destination_coords,
        "using_poseidon": using_poseidon
    })


@client.tree.command()
@app_commands.describe(**CLOSEST_CITY_TO_TARGET_DESCRIPTION)
async def closest_city_to_target(interaction: discord.Interaction, player_name: str, coords: str):
    """Checks which of the player's city is the closest to the target island"""
    await run_command(interaction, ClosestCityToTarget, {
        "player_name": player_name,
        "coords": coords
    })


client.run(BOT_TOKEN)
