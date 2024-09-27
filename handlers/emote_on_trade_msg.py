import json
import re
from datetime import datetime, timedelta

import discord

from utils.constants import TRADE_HISTORY_FILE_PATH, RESOURCE_EMOJIS, TRADE_REG_PATTERN
from utils.general_utils import create_embed


def load_trade_history():
    """Load trade history from the JSON file."""
    try:
        with open(TRADE_HISTORY_FILE_PATH, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty trade history if file is missing or corrupted


def save_trade_history(trade_history):
    """Save trade history to the JSON file."""
    with open(TRADE_HISTORY_FILE_PATH, 'w') as file:
        json.dump(trade_history, file, indent=4, default=str)  # Save datetime as string


def track_trade(guild_id, user_id, offer, want):
    """Track a new trade for a guild in the trade history."""
    trade_history = load_trade_history()

    # Convert guild_id and user_id to strings
    guild_id_str = str(guild_id)
    user_id_str = str(user_id)

    # Debugging: Print loaded trade history
    print(f"Loaded Trade History: {trade_history}")  # Show current trade history

    # Check if the guild_id exists, if not, create an entry
    if guild_id_str not in trade_history:
        print(f"Guild ID {guild_id_str} not found, creating new entry.")
        trade_history[guild_id_str] = {}

    # Check if the user_id exists within the guild_id, if not, create an entry
    if user_id_str not in trade_history[guild_id_str]:
        print(f"User ID {user_id_str} not found for guild {guild_id_str}, creating new entry.")
        trade_history[guild_id_str][user_id_str] = []

    # Append the new trade
    trade_history[guild_id_str][user_id_str].append({
        "offer": offer,
        "want": want,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M")  # Format the timestamp
    })

    # Debugging: Print the updated trade history
    print(f"Updated Trade History: {trade_history}")  # Show updated trade history

    save_trade_history(trade_history)


def check_for_trade_match(guild_id, user_id, offer, want):
    """Check if there's a matching trade within the guild's trade history."""
    trade_history = load_trade_history()

    # Convert IDs to strings for comparison
    guild_id_str = str(guild_id)
    user_id_str = str(user_id)

    # Check if the guild exists in the trade history
    if guild_id_str not in trade_history:
        return None, None  # No trades in this guild yet

    current_time = datetime.utcnow()
    guild_trades = trade_history[guild_id_str]

    # Filter out expired trades
    expired_traders = []
    for trader_id, trades in guild_trades.items():
        # Remove expired trades for this user
        trades = [trade for trade in trades if current_time - datetime.fromisoformat(trade['timestamp']) <= timedelta(hours=24)]
        if not trades:  # If no trades left, mark for deletion
            expired_traders.append(trader_id)
        else:
            guild_trades[trader_id] = trades  # Update the list of trades for active users

    # Remove expired traders
    for trader_id in expired_traders:
        del guild_trades[trader_id]

    # Save updated trade history after cleanup
    trade_history[guild_id_str] = guild_trades
    save_trade_history(trade_history)

    # Check for a matching trade
    for trader_id, trades in guild_trades.items():
        # skip if the trade was posted by the same person
        if trader_id == user_id_str:
            continue

        for trade in trades:
            # Check if the trades match (offer and want swapped)
            if trade["want"] == offer and trade["offer"] == want:
                return trader_id, trade

    return None, None  # No match found


async def check_msg_for_trade_offer(message: discord.Message, bot):
    trade_msg = re.match(TRADE_REG_PATTERN, message.content.lower(), re.IGNORECASE)
    if trade_msg:
        offer = trade_msg.group(1).strip()
        want = trade_msg.group(2).strip()

        offer_with_emojis = convert_to_emojis(offer)
        want_with_emojis = convert_to_emojis(want)

        embed = create_embed(description=f"{message.author.mention} is looking to trade: {offer_with_emojis} for {want_with_emojis}")
        embed.set_footer(
            text=f"This offer will expire in 1 day. Post your own offer by typing 'Trade: (resource1) for (resource2)' "
                 f"or message {message.author.name} directly to notify them about the trade"
        )

        await message.delete()
        await message.channel.send(embed=embed)

        # Record the trade in the JSON file under the guild ID
        track_trade(message.guild.id, message.author.id, offer, want)

        # Check for matching trade offers
        matched_user_id, matched_trade = check_for_trade_match(message.guild.id, message.author.id, offer, want)
        if matched_user_id:
            await dm_user(bot, message.author.id, matched_user_id, matched_trade)
            await dm_user(bot, matched_user_id, message.author.id, {"offer": offer, "want": want})


async def dm_user(bot, trade_poster_id: int, matching_trade_poster_id: int, trade: dict):
    trade_poster = await bot.fetch_user(trade_poster_id)

    # Create a mention for the matching trade poster
    matching_trade_poster_mention = f"<@{matching_trade_poster_id}>"

    await trade_poster.send(embed=create_embed(
        "A matching trade was found!",
        f"{matching_trade_poster_mention} is offering {trade['offer']} for {trade['want']}",
        discord.Color.green()
    ))


def convert_to_emojis(resource_list):
    # Split the resources (comma-separated)
    resources = [res.strip() for res in resource_list.split(",")]
    # Convert to emoji if available, otherwise keep the original name
    return ", ".join([RESOURCE_EMOJIS.get(res.lower(), res) for res in resources])
