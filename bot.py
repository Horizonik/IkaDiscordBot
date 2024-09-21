import os

from discord.ext import commands

from commands.calculate_clusters import CalculateClusters
from commands.generate_heatmap import GenerateHeatmap

# Discord bot setup
bot = commands.Bot(command_prefix='!')
BOT_TOKEN = os.getenv('BOT_TOKEN')


async def run_command(command_class, command_author_name: str, command_params: dict):
    """Dynamically run the logic for a given command"""
    command_class_instance = command_class(command_author_name, command_params)
    await command_class_instance.run()


@bot.command()
async def calculate_clusters(ctx, min_cities: int):
    await run_command(
        CalculateClusters,
        ctx.author.name,
        {"min_cities": min_cities}
    )


@bot.command()
async def generate_heatmap(ctx, alliance_name: str, min_cities_on_island: int):
    await run_command(
        GenerateHeatmap,
        ctx.author.name,
        {"alliance_name": alliance_name, "min_cities": min_cities_on_island}
    )


bot.run(BOT_TOKEN)
