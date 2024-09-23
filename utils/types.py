import datetime
import traceback
from enum import Enum

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
            stack_trace = traceback.format_exc()  # Capture the stack trace
            print(f"{datetime.datetime.now()} | An error occurred while executing command '{self.ctx.command.name}': {str(e)}\n{stack_trace}")
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}. If this issue persists, please yell at my creator.",
                color=discord.Color.red()
            )
            await self.ctx.response.send_message(embed=embed)

        finally:
            await self.log_at_run_end()

    async def command_logic(self):
        """This should be implemented in subclasses"""
        raise NotImplementedError("Subclasses must implement command_logic method.")


class ResourceType(Enum):
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
        raise ValueError(f"No ResourceType found for value: {value}")


class WonderType(Enum):
    """Converts the numeric value from the 'trade-good' var into the string type of the island."""
    FORGE = 1
    HADES = 2
    DEMETER = 3
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


class UnitType(Enum):
    GYROCOPTER = "Gyrocopter"
    DOCTOR = "Doctor"
    ARCHER = "Archer"
    HOPLITE = "Hoplite"
    SLINGER = "Slinger"
    SPEARMAN = "Spearman"
    SULPHUR_CARABINEER = "Sulphur Carabineer"
    SWORDSMAN = "Swordsman"
    CATAPULT = "Catapult"
    COOK = "Cook"
    MORTAR = "Mortar"
    RAM = "Ram"
    STEAM_GIANT = "Steam Giant"
    BALLOON_BOMBARDIER = "Balloon Bombardier"
    STEAM_RAM = "Steam Ram"
    FIRE_SHIP = "Fire Ship"
    RAM_SHIP = "Ram Ship"
    BALLISTA_SHIP = "Ballista Ship"
    CATAPULT_SHIP = "Catapult Ship"
    MORTAR_SHIP = "Mortar Ship"
    ROCKET_SHIP = "Rocket Ship"
    SUBMARINE = "Submarine"
    BALLOON_SHIP = "Balloon Ship"
    PADDLE_SPEEDBOAT = "Paddle Speedboat"
    TENDER = "Tender"


class CityInfo:
    coords: tuple[int, int]
    x: int
    y: int

    tradegood: int  # the ID of the resource of the island
    resource_type: str  # the str name of the resource of the island
    wood_level: int  # the level of the island's wood mine
    resource_level: int  # the level of the island's resource mine
    island_name: str

    wonder: int  # the ID of the wonder of the island
    wonder_type: str  # the str name of the wonder of the island
    wonder_level: int  # the level of the island's wonder

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
        setattr(self, 'resource_type', ResourceType.from_value(data['tradegood']))

        # Convert wonder ID to a string identification of the wonder
        setattr(self, 'wonder_type', WonderType.from_value(data['wonder']))

        # Put x,y coords into a tuple for ease of use later on
        setattr(self, 'coords', (data['x'], data['y']))

        # Change names from the Ika-logs names to better ones
        self.resource_level = data['island_tradegood'] if 'island_tradegood' in data else data['resource_level']
        self.wonder_level = data['island_wonder'] if 'island_wonder' in data else data['wonder_level']
        self.wood_level = data['island_wood'] if 'island_wonder' in data else data['wood_level']

    def __repr__(self):
        return (
            f"<CityInfo(name={self.player_name}, "
            f"coords={self.coords}, "
            f"tradegood={self.resource_type}, "
            f"score={self.player_score}, "
            f"level={self.city_level})>"
        )


class IslandInfo:
    coords: tuple[int, int]
    name: str
    tier: str
    x: int
    y: int

    cities: list[CityInfo]

    wood_level: int

    resource_type: str
    resource_level: int

    wonder_type: str
    wonder_level: int

    def __init__(self, data: dict, cities: list[CityInfo] = None):
        # Automatically grab class annotations (aka attributes)
        for attr, attr_type in self.__annotations__.items():
            if attr in data:
                setattr(self, attr, data[attr])

        if cities:
            self.cities = cities

        self.name = data['island_name'] if 'island_name' in data else data['name']

    def __repr__(self):
        return (
            f"<IslandInfo=[{self.coords}], "
            f"WONDER={self.wonder_type} [{self.wonder_level}], "
            f"RES={self.resource_type} [{self.resource_level}], "
            f"WOOD=[{self.wood_level}]>"
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
            f"{datetime.datetime.now()} | Logged in as {self.user} (ID: {self.user.id}) \n"
            "------"
        )

    async def on_disconnect(self):
        print(
            f"{datetime.datetime.now()} | Disconnected from Discord, or a connection attempt to Discord has failed, \n"
            "this could happen either through the internet being disconnected or explicit calls being too close. \n"
            "------"
        )

    async def on_connect(self):
        print(f"{datetime.datetime.now()} | Successfully connected to Discord Services")
