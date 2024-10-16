from datetime import datetime

import discord
from discord import app_commands

from commands.calculate_clusters import CalculateClusters
from commands.closest_city_to_target import ClosestCityToTarget
from commands.find_island import FindIsland
from commands.find_player import FindPlayer
from commands.help import HelpCommand
from commands.list_best_islands import ListBestIslands
from commands.manage_settings import ResetSettings, ShowSettings, UpdateSetting
from commands.travel_time import CalculateTravelTime
from database.guild_settings_manager import fetch_or_create_settings
from embeds.embeds import welcome_message_embed
from handlers.trade_matcher import check_msg_for_trade_offer
from utils.constants import (
    CALCULATE_CLUSTERS_DESCRIPTION,
    FIND_PLAYER_DESCRIPTION,
    TRAVEL_TIME_DESCRIPTION,
    CLOSEST_CITY_TO_TARGET_DESCRIPTION,
    LIST_BEST_ISLANDS_DESCRIPTION,
    BOT_TOKEN,
    CHANGE_SETTING_DESCRIPTION, FIND_ISLAND_DESCRIPTION
)
from utils.types import WonderType, ResourceType, UnitType, ConfigurableSetting, ClosestCitySearchTypes


class DiscordBotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands globally to all servers the bot is in
        await self.tree.sync()

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Ikariam"))
        print(
            f"{datetime.now()} | Logged in as {self.user} (ID: {self.user.id}) \n"
            "------"
        )

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        # Call the trade checking logic
        await check_msg_for_trade_offer(message, self)

    async def on_connect(self):
        print(f"{datetime.now()} | Successfully connected to Discord Services")

    async def on_guild_join(self, guild: discord.Guild):

        # Check if the server already has existing settings, if not, initialize them
        fetch_or_create_settings(guild)

        # Send a greeting message
        greeting_message = welcome_message_embed(guild)

        if guild.system_channel:
            await guild.system_channel.send(embed=greeting_message)


client = DiscordBotClient()


async def run_command(interaction: discord.Interaction, command_class, command_params: dict = None):
    """Dynamically run the logic for a given command and allow sending a response"""
    if command_params is None:
        command_params = {}

    # Check if the server already has existing settings, if not, initialize them
    settings = fetch_or_create_settings(interaction.guild)

    # Create an instance of the command class and run it
    command_class_instance = command_class(interaction, command_params, settings)
    await command_class_instance.run()


###
# COMMANDS
###
@client.tree.command()
@app_commands.describe(**CALCULATE_CLUSTERS_DESCRIPTION)
async def calculate_clusters(interaction: discord.Interaction, alliance_name: str, min_cities_per_island: int,
                             max_cluster_distance: int, min_cities_per_cluster: int):
    """Calculates which island groups (clusters) have the most cities from the selected alliance"""
    await run_command(interaction, CalculateClusters, {
        'alliance_name': alliance_name,
        'min_cities_per_island': min_cities_per_island,
        'max_cluster_distance': max_cluster_distance,
        'min_cities_per_cluster': min_cities_per_cluster
    })


@client.tree.command()
@app_commands.describe(**FIND_PLAYER_DESCRIPTION)
async def find_player(interaction: discord.Interaction, player_name: str, alliance_name: str = None):
    """Retrieves information about the player's cities locations"""
    await run_command(interaction, FindPlayer, {"player_name": player_name.lower(), "alliance_name": alliance_name})


@client.tree.command()
@app_commands.describe(**FIND_ISLAND_DESCRIPTION)
async def find_island(interaction: discord.Interaction, coords: str):
    """Retrieves information about the island"""
    await run_command(interaction, FindIsland, {"coords": coords})


@client.tree.command()
@app_commands.describe(**TRAVEL_TIME_DESCRIPTION)
async def travel_time(
        interaction: discord.Interaction, unit_type: UnitType, start_coords: str, destination_coords: str,
        using_poseidon: bool = False, using_oligarchy: bool = False, sea_chart_level: int = 0
):
    """Calculates estimated travel time for units based on type and coordinates (data is based on the ikariam wiki, might not be 100% accurate!)"""
    await run_command(interaction, CalculateTravelTime, {
        "unit_type": unit_type,
        "start_coords": start_coords,
        "destination_coords": destination_coords,
        "using_poseidon": using_poseidon,
        "using_oligarchy": using_oligarchy,
        "sea_chart_level": sea_chart_level,
    })


@client.tree.command()
@app_commands.describe(**CLOSEST_CITY_TO_TARGET_DESCRIPTION)
async def closest_city_to_target(interaction: discord.Interaction, search_type: ClosestCitySearchTypes, name: str, coords: str):
    """Checks which of the player's/alliance cities is the closest to the target island"""
    await run_command(interaction, ClosestCityToTarget, {
        "search_type": search_type,
        "name": name.lower(),
        "coords": coords
    })


@client.tree.command()
@app_commands.describe(**LIST_BEST_ISLANDS_DESCRIPTION)
async def list_best_islands(interaction: discord.Interaction, resource_type: ResourceType, miracle_type: WonderType,
                            no_full_islands: bool = True):
    """
    If available for your world, goes over the islands and attempts to find the best match based on your filters
    """
    await run_command(interaction, ListBestIslands, {
        "resource_type": resource_type,
        "miracle_type": miracle_type,
        "no_full_islands": no_full_islands
    })


###
# Manage Settings Commands
###
@client.tree.command()
@app_commands.describe(**CHANGE_SETTING_DESCRIPTION)
@app_commands.checks.has_permissions(administrator=True)
async def change_setting(interaction: discord.Interaction, setting: ConfigurableSetting, new_value: str):
    """Change a setting and give it a new value"""
    await run_command(interaction, UpdateSetting, {
        "setting_name": setting.name,
        "new_value": new_value
    })


@client.tree.command()
@app_commands.checks.has_permissions(administrator=True)
async def show_settings(interaction: discord.Interaction):
    """View your server's current settings"""
    await run_command(interaction, ShowSettings, {})


@client.tree.command()
@app_commands.checks.has_permissions(administrator=True)
async def reset_settings(interaction: discord.Interaction):
    """This will reset your server's settings to the default preset"""
    await run_command(interaction, ResetSettings, {})


# Handle permission errors
@change_setting.error
@show_settings.error
@reset_settings.error
async def permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(
            embed=create_embed(
                "You do not have permission to use this command. Only administrators can configure my settings.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )


@client.tree.command()
async def help(interaction: discord.Interaction):
    """Displays a dynamic help menu with all available commands."""
    await run_command(interaction, HelpCommand, {})


client.run(BOT_TOKEN)
