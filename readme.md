# IkaDiscordBot

A utility discord bot that fetches data from IkaLogs, processes it and is able to calculate complicated things based on
it. The bot produces a variety of useful information that is focused on targeting opponents and ways of attack within
the game.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

```
# Clone the repository
git clone https://github.com/yourusername/ikariam-discord-bot.git

# Navigate to the project directory
cd ikariam-discord-bot

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the required dependencies
pip install -r requirements.txt

# Set your Discord bot token as an environment variable
export BOT_TOKEN=your_discord_bot_token  # On Windows: set BOT_TOKEN=your_discord_bot_token

# Start the bot
python bot.py
```

## Usage

1. Invite the bot to your discord server.
2. Restart your discord to make sure the commands are updated on your end.
3. Once the restart is complete, you can type '/' and the autocomplete will show you all the
   bot's commands.

## Commands Overview

This Discord bot includes the following commands:

- **/calculate_clusters**: Calculates island groups with the most cities from a selected alliance.
- **/find_player**: Retrieves information about a player's city locations.
- **/find_island**: Retrieves information about an island based on coordinates.
- **/travel_time**: Calculates estimated travel time for units based on type and coordinates.
- **/closest_city_to_target**: Finds the closest city to a target island.
- **/list_best_islands**: Finds the best islands based on filters.
- **/change_setting**: Change a setting and give it a new value (admin only).
- **/show_settings**: View current server settings (admin only).
- **/reset_settings**: Reset server settings to default (admin only).
- **/help**: Displays a dynamic help menu with all available commands.

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-foo`)
3. Make your changes and commit them (`git commit -am 'Add some foo'`)
4. Push to the branch (`git push origin feature-foo`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details

## Contact

Horizonik - [ofekyvb@gmail.com](mailto:ofekyvb@gmail.com)

Project Link - [https://github.com/Horizonik/IkaDiscordBot](https://github.com/Horizonik/IkaDiscordBot)
