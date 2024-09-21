import os
import discord
from discord import app_commands
from commands.calculate_clusters import CalculateClusters
from commands.travel_time import CalculateTravelTime
from commands.find_player import FindPlayer
from commands.generate_heatmap import GenerateHeatmap
from commands.command_descriptions import (
    calculate_clusters_description,
    generate_heatmap_description,
    find_player_description,
    travel_time_description
)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands globally to all servers the bot is in
        await self.tree.sync()


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = MyClient(intents=intents)
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


#####
# COMMANDS
#####
@client.tree.command()
@app_commands.describe(**calculate_clusters_description)
async def calculate_clusters(
        interaction: discord.Interaction,
        alliance_name: str,
        min_cities_per_island: int,
        max_cluster_distance: int,
        min_cities_per_cluster: int
):
    """Calculates clusters based on the minimum number of cities"""
    await run_command(interaction, CalculateClusters, {
        'alliance_name': alliance_name,
        'min_cities_per_island': min_cities_per_island,
        'max_cluster_distance': max_cluster_distance,
        'min_cities_per_cluster': min_cities_per_cluster
    })


@client.tree.command()
@app_commands.describe(**generate_heatmap_description)
async def generate_heatmap(interaction: discord.Interaction, alliance_name: str, min_cities_on_island: int):
    """Generates a heatmap based on the alliance and minimum cities"""
    await run_command(interaction, GenerateHeatmap,
                      {"alliance_name": alliance_name, "min_cities": min_cities_on_island})


@client.tree.command()
@app_commands.describe(**find_player_description)
async def find_player(interaction: discord.Interaction, player_name: str, alliance_name: str = None):
    """Generates a heatmap based on the alliance and minimum cities"""
    await run_command(interaction, FindPlayer, {"player_name": player_name, "alliance_name": alliance_name})


@client.tree.command()
@app_commands.describe(**travel_time_description)
async def travel_time(
        interaction: discord.Interaction,
        unit_type: str, start_coords: str,
        destination_coords: str,
        using_poseidon: bool = False
):
    """Calculates estimated travel time for units based on type and coordinates"""
    await run_command(interaction, CalculateTravelTime, {
        "unit_type": unit_type,
        "start_coords": start_coords,
        "destination_coords": destination_coords,
        "using_poseidon": using_poseidon
    })


# Run the bot
client.run(BOT_TOKEN)
