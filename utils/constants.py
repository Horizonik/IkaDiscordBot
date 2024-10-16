import os

from utils.types import WonderType, UnitType

# - General Settings -
DATA_FETCH_BASE_URL = 'https://ikalogs.ru/common/report/index/'  # link to call to obtain data from ika-logs
BOT_TOKEN = os.getenv('BOT_TOKEN')  # discord app token
BOT_ENV = str(os.getenv('BOT_ENV'))  # 'dev' or 'prod'

# - File Paths -
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
DEFAULT_SETTINGS_FILE_PATH = os.path.join(BASE_DIR, 'settings', 'default_settings.json')  # A set of default settings to fall back to

# - Configurations -
GOOD_WONDERS = [WonderType.POSEIDON, WonderType.FORGE]
TRADE_REG_PATTERN = r"trade:\s*(.*)\s*for\s*(.*)"

# - Bot Emojis Mappings -
e_advisor_bloated = '<:advisor_bloated:1287019312103686302>'
e_citizen_head = '<:citizen_head:1287019270513102948>'
e_very_outraged = '<:very_outraged:1287536914160816128>'
e_ecstatic = ' <:ecstatic:1287536875938123839>'
e_outraged = ' <:outraged:1287536862075945030>'

BOT_EMJOIS = {
    "marble": '<:marble:1289267605055475762>',
    "wood": '<:wood:1289267533484134400>',
    "wine": '<:wine:1289267622931599441>',
    "sulphur": '<:sulphur:1289267553071267880>',
    "crystal": '<:crystal:1289267588425191464>',
    "gold": '<:gold:1289267640149348372>',
}

# - Unit Speeds -
unit_speeds = {
    UnitType.GYROCOPTER: 60,
    UnitType.DOCTOR: 48,
    UnitType.ARCHER: 48,
    UnitType.HOPLITE: 48,
    UnitType.SLINGER: 48,
    UnitType.SPEARMAN: 48,
    UnitType.SULPHUR_CARABINEER: 48,
    UnitType.SWORDSMAN: 48,
    UnitType.CATAPULT: 30,
    UnitType.COOK: 30,
    UnitType.MORTAR: 30,
    UnitType.RAM: 30,
    UnitType.STEAM_GIANT: 30,
    UnitType.BALLOON_BOMBARDIER: 15,
    UnitType.STEAM_RAM: 40,
    UnitType.FIRE_SHIP: 40,
    UnitType.RAM_SHIP: 40,
    UnitType.BALLISTA_SHIP: 40,
    UnitType.CATAPULT_SHIP: 40,
    UnitType.MORTAR_SHIP: 30,
    UnitType.ROCKET_SHIP: 30,
    UnitType.SUBMARINE: 40,
    UnitType.BALLOON_SHIP: 20,
    UnitType.PADDLE_SPEEDBOAT: 60,
    UnitType.TENDER: 30,
}

ship_units = {
    UnitType.STEAM_RAM,
    UnitType.FIRE_SHIP,
    UnitType.RAM_SHIP,
    UnitType.BALLISTA_SHIP,
    UnitType.CATAPULT_SHIP,
    UnitType.MORTAR_SHIP,
    UnitType.ROCKET_SHIP,
    UnitType.SUBMARINE,
    UnitType.BALLOON_SHIP,
    UnitType.PADDLE_SPEEDBOAT,
    UnitType.TENDER
}

# - Parameter descriptions for every command -
# These are imported into bot.py for use with discord.py
CALCULATE_CLUSTERS_DESCRIPTION = {
    "alliance_name": "Name of the alliance to calculate clusters for",
    "min_cities_per_island": "Minimum number of cities required on an island for it to be included",
    "max_cluster_distance": "Maximum distance between islands to be considered in the same cluster",
    "min_cities_per_cluster": "Minimum amount of cities required for a cluster to be included"
}

GENERATE_HEATMAP_DESCRIPTION = {
    "alliance_name": "Name of the alliance",
    "min_cities_on_island": "Minimum cities on an island"
}

FIND_PLAYER_DESCRIPTION = {
    "player_name": "The name of the player",
    "alliance_name": "Optional - Name of the alliance the player belongs to"
}

FIND_ISLAND_DESCRIPTION = {
    "coords": "The location of the island (in X:Y format)",
}

TRAVEL_TIME_DESCRIPTION = {
    "unit_type": "LAND/SEA",
    "start_coords": "The coords that the units come from",
    "destination_coords": "The desired destination for the units",
    "using_poseidon": "Are you using the Poseidon miracle (100% reduction)?"
}

CLOSEST_CITY_TO_TARGET_DESCRIPTION = {
    "search_type": "The type of search you'd like to make. If 'alliance', will search for closest ally city, if 'player', will search for closest player city.",
    "name": "The name of the player/alliance depending on what you chose at search_type",
    "coords": "The target location to which we will compare city distances of the selected player"
}

LIST_BEST_ISLANDS_DESCRIPTION = {
    "resource_type": "Filter for islands that only contain this specific resource",
    "miracle_type": "Filter for islands that only contain this specific miracle",
    "no_full_islands": "Do you want to see full islands in the results? Default true.",
}

CHANGE_SETTING_DESCRIPTION = {
    "setting": "The setting to change",
    "new_value": "The new value for the setting"
}
