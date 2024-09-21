from enum import Enum

import datetime
import discord
from discord import app_commands


class BaseCommand:
    """This class implements the basics that every command requires"""
    ctx: discord.Interaction
    command_params: dict
    command_start_time: datetime.datetime

    def __init__(self, ctx: discord.Interaction, command_params: dict):
        # Gather basic information about queued command run
        self.ctx = ctx
        self.command_params = command_params
        self.command_start_time = datetime.datetime.now()

    async def log_at_run_end(self):
        print(f"{datetime.datetime.now()} | Finished running the '{self.ctx.command.name}' command!")

    async def run(self):
        """Run logic for the command"""
        print(f"{self.command_start_time} | User {self.ctx.user.name} ran the '{self.ctx.command.name}' command with params {self.command_params}")
        await self.execute_with_logging()

    async def execute_with_logging(self):
        """Execute the command logic and log after completion."""
        try:
            await self.command_logic()  # Call the logic defined in subclasses

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await self.ctx.response.send_message(embed=embed)

        finally:
            await self.log_at_run_end()

    async def command_logic(self):
        """This should be implemented in subclasses"""
        raise NotImplementedError("Subclasses must implement command_logic method.")


class IslandTypes(Enum):
    """Converts the numeric value from the 'trade-good' var into the string type of the island."""
    VINE = 1
    MARBLE = 2
    CRYSTAL = 3
    SULPHUR = 4

    def __str__(self):
        return self.name.lower()  # Returns the name in lowercase

    @classmethod
    def from_value(cls, value):
        """Get the string name for a given numeric value."""
        for island in cls:
            if island.value == value:
                return str(island)
        raise ValueError(f"No IslandType found for value: {value}")


class WonderTypes(Enum):
    """Converts the numeric value from the 'trade-good' var into the string type of the island."""
    FORGE = 1
    HADES = 2
    DEMETERS = 3
    ATHENA = 4
    HERMES = 5
    ARES = 6
    POSEIDON = 7
    COLOSSUS = 8

    def __str__(self):
        return self.name.lower()  # Returns the name in lowercase

    @classmethod
    def from_value(cls, value):
        """Get the string name for a given numeric value."""
        for miracle in cls:
            if miracle.value == value:
                return str(miracle)
        raise ValueError(f"No WonderType found for value: {value}")


class CityInfo:
    coords: tuple[int, int]
    x: int
    y: int

    tradegood: int  # the ID of the resource of the island
    tradegood_type: str  # the str name of the resource of the island
    island_wood: int  # the level of the island's wood mine
    island_tradegood: int  # the level of the island's resource mine

    wonder: int  # the ID of the wonder of the island
    wonder_type: str  # the str name of the wonder of the island
    island_wonder: int  # the level of the island's wonder

    city_level: int
    city_name: str

    player_name: str
    player_score: int

    def __init__(self, data: dict):
        # Automatically grab class annotations (aka attributes)
        for attr, attr_type in self.__annotations__.items():
            if attr in data:
                setattr(self, attr, data[attr])

        # Convert trade-good ID to a string identification of the trade-good
        setattr(self, 'tradegood_type', IslandTypes.from_value(data['tradegood']))

        # Convert wonder ID to a string identification of the wonder
        setattr(self, 'wonder_type', WonderTypes.from_value(data['wonder']))

        # Put x,y coords into a tuple for ease of use later on
        setattr(self, 'coords', (data['x'], data['y']))

    def __repr__(self):
        return (
            f"<CityInfo(name={self.player_name}, "
            f"coords={self.coords}, "
            f"tradegood={self.tradegood_type}, "
            f"score={self.player_score}, "
            f"level={self.city_level})>"
        )


class IslandInfo:
    coords: tuple[int, int]
    x: int
    y: int

    resource_type: IslandTypes
    resource_level: int
    wood_level: int
    wonder_level: int

    def __init__(self, data: dict):
        # Automatically grab class annotations (aka attributes)
        for attr, attr_type in self.__annotations__.items():
            if attr in data:
                setattr(self, attr, data[attr])

    def __repr__(self):
        return (
            f"<IslandInfo(coords={self.coords}, "
            f"resource_type={self.resource_type}, "
            f"resource_level={self.resource_level}, "
            f"wood_level={self.wood_level}, "
            f"wonder_level={self.wonder_level})>"
        )


class ClusterInfo:
    name: str
    rating: int  # Score on how good are the cities in this cluster altogether
    cities: list[CityInfo]
    islands: list[IslandInfo]

    def __init__(self, name: str, rating: int, cities: list[CityInfo], islands: list[IslandInfo] = None):
        self.name = name
        self.rating = rating
        self.cities = cities  # List of CityInfo instances
        self.islands = islands  # List of IslandInfo instances

    def __repr__(self) -> str:
        return (
            f"<ClusterInfo(name={self.name}, "
            f"rating={self.rating}, "
            f"cities_count={len(self.cities)}, "
            f"islands_count={len(self.islands)})>"
        )


class DiscordBotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands globally to all servers the bot is in
        await self.tree.sync()
