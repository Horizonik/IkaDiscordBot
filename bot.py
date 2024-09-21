import os
import discord
from discord import app_commands
from commands.calculate_clusters import CalculateClusters
from commands.travel_time import CalculateTravelTime
from commands.find_player import FindPlayer
from commands.generate_heatmap import GenerateHeatmap
from commands.test import TestMessage, TestImage, TestEmbed


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands globally to all servers the bot is in
        await self.tree.sync()


# Define the bot's intents
intents = discord.Intents.default()
intents.messages = True  # If you need to listen to messages
intents.message_content = True

client = MyClient(intents=intents)
BOT_TOKEN = os.getenv('BOT_TOKEN')


async def run_command(interaction, command_class, command_params: dict = None):
    """Dynamically run the logic for a given command and allow sending a response"""
    if command_params is None:
        command_params = {}

    # Create an instance of the command class and run it
    command_class_instance = command_class(interaction, command_params)
    await command_class_instance.run()


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


#####
# TEST COMMANDS
#####
@client.tree.command()
async def test_message(interaction: discord.Interaction):
    """Sends a test message"""
    await run_command(interaction, TestMessage)


@client.tree.command()
async def test_embed(interaction: discord.Interaction):
    """Sends a test embed"""
    await run_command(interaction, TestEmbed)


@client.tree.command()
async def test_image(interaction: discord.Interaction):
    """Sends a test image"""
    await run_command(interaction, TestImage)


#####
# PRACTICAL COMMANDS
#####
@client.tree.command()
@app_commands.describe(
    alliance_name="Name of the alliance to calculate clusters for",
    min_cities_per_island="Minimum number of cities required on an island for it to be included",
    max_cluster_distance="Maximum distance between islands to be considered in the same cluster",
    min_cities_per_cluster="Minimum amount of cities required for a cluster to be included"
)
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
@app_commands.describe(
    alliance_name="Name of the alliance",
    min_cities_on_island="Minimum cities on an island"
)
async def generate_heatmap(interaction: discord.Interaction, alliance_name: str, min_cities_on_island: int):
    """Generates a heatmap based on the alliance and minimum cities"""
    await run_command(interaction, GenerateHeatmap,
                      {"alliance_name": alliance_name, "min_cities": min_cities_on_island})


@client.tree.command()
@app_commands.describe(
    player_name="The name of the player",
    alliance_name="Optional - Name of the alliance the player belongs to"
)
async def find_player(interaction: discord.Interaction, player_name: str, alliance_name: str = None):
    """Generates a heatmap based on the alliance and minimum cities"""
    await run_command(interaction, FindPlayer, {"player_name": player_name, "alliance_name": alliance_name})


@client.tree.command()
@app_commands.describe(
    unit_type="LAND/SEA",
    start_coords="The coords that the units come from",
    destination_coords="The desired destination for the units",
    using_poseidon="Are you using the Poseidon miracle (100% reduction)?"
)
async def travel_time(
        interaction: discord.Interaction,
        unit_type: str, start_coords: str,
        destination_coords: str,
        using_poseidon: bool = False
):
    """Calculates estimated travel time for units based on type and coordinates"""
    # Validate unit type
    if unit_type.lower() not in ["land", "sea"]:
        await interaction.response.send_message("Invalid unit type! Please use 'land' or 'sea'.")
        return

    # Validate and parse start coordinates
    try:
        start_x, start_y = map(int, start_coords.split(':'))
        dest_x, dest_y = map(int, destination_coords.split(':'))
    except ValueError:
        await interaction.response.send_message("Invalid start coordinates format! Please use 'X:Y'.")
        return

    await run_command(interaction, CalculateTravelTime, {
        "unit_type": unit_type.lower(),
        "start_coords": (start_x, start_y),
        "destination_coords": (dest_x, dest_y),
        "using_poseidon": using_poseidon
    })


# Run the bot
client.run(BOT_TOKEN)
