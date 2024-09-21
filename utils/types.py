from contextlib import contextmanager
from enum import Enum
from typing import Any
import datetime


class BaseCommand:
    """This class implements the basics that every command requires"""
    command_initiator_name: str
    command_name: str
    command_params: dict
    command_start_time: datetime

    def __init__(self, command_initiator_name: str, command_name: str):
        # Gather basic information about queued command run
        self.command_initiator_name = command_initiator_name
        self.command_name = command_name
        self.command_start_time = datetime.datetime.now()

    def log_at_run_end(self):
        print(f"{datetime.datetime.now()} | Finished running the '{self.command_name}' command!")

    def run(self) -> Any:
        """Run logic for the command"""
        print(
            f"{self.command_start_time} | User {self.command_initiator_name} ran the '{self.command_name}' command with params {self.command_params}")
        self.execute_with_logging()

    def execute_with_logging(self):
        """Execute the command logic and log after completion."""
        try:
            self.command_logic()  # Call the logic defined in subclasses
        finally:
            self.log_at_run_end()

    def command_logic(self):
        """This should be implemented in subclasses"""
        raise NotImplementedError("Subclasses must implement command_logic method.")


class IslandTypes(Enum):
    """Converts the numeric value from the 'trade-good' var into the string type of the island"""
    VINE = 1
    MARBLE = 2
    CRYSTAL = 3
    SULPHUR = 4


class CityInfo:
    coords: tuple[int, int]
    x: int
    y: int

    tradegood: int
    tradegood_type: IslandTypes
    island_wood: int
    island_tradegood: int
    island_wonder: int
    city_level: int

    player_name: str
    player_score: int

    def __init__(self, data: dict):
        # Automatically grab class annotations (aka attributes)
        for attr, attr_type in self.__annotations__.items():
            if attr in data:
                setattr(self, attr, data[attr])

        # Convert trade-good ID to a string identification of the trade-good
        setattr(self, 'tradegood_type', IslandTypes(data['tradegood']))

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

    def __init__(self, name: str, rating: int, cities: list[CityInfo], islands: list[IslandInfo]):
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
