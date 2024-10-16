import re

import discord

from database.guild_settings_manager import run_query
from embeds.embeds import trade_offer_embed, trade_dm_embed
from utils.constants import TRADE_REG_PATTERN, BOT_ENV
from utils.general_utils import convert_to_emojis


def find_matching_trades(guild: discord.Guild, trade_offer_author: discord.User, trade_have: str, trade_want: str) -> list[dict]:
    """load trade history from the last day"""
    return run_query(f"""
        SELECT * FROM {BOT_ENV}_trades_history 
        WHERE proposal_time >= datetime('now', '-1 day')
            AND guild_id = {guild.id}
            AND proposer_id != {trade_offer_author.id}
            AND (have = '{trade_want}' AND want = '{trade_have}')   
    """)


def save_new_trade_offer(guild: discord.Guild, trade_offer_author: discord.User, trade_have: str, trade_want: str):
    """Insert a new trade offer to the db"""

    run_query(f"""
        INSERT INTO {BOT_ENV}_trades_history (guild_id, proposer_id, have, want)
        VALUES ({guild.id}, {trade_offer_author.id}, '{trade_have}', '{trade_want}')
    """)


async def check_msg_for_trade_offer(message: discord.Message, bot_self):
    trade_msg = re.match(TRADE_REG_PATTERN, message.content.lower(), re.IGNORECASE)
    if not trade_msg:
        return

    have = trade_msg.group(1).strip()
    want = trade_msg.group(2).strip()

    offer_with_emojis = convert_to_emojis(have)
    want_with_emojis = convert_to_emojis(want)

    embed = trade_offer_embed(offer_with_emojis, want_with_emojis, message.author)

    # Delete user message, post embed instead
    await message.delete()
    await message.channel.send(embed=embed)

    # Check for a matching trade
    trade_offers_from_last_day = find_matching_trades(message.guild, message.author, have, want)
    if trade_offers_from_last_day:
        for trade in trade_offers_from_last_day:
            await dm_user_about_trade(bot_self, message.author.id, trade['user_id'], trade)
            await dm_user_about_trade(bot_self, trade['user_id'], message.author.id, {"have": trade['have'], "want": trade['want']})

        # Remove the finished trades from the database
        delete_concluded_trades(trade_offers_from_last_day)

    # No matching trade found - add the trade to the db for tracking
    else:
        save_new_trade_offer(message.guild, message.author, have, want)


def delete_concluded_trades(trade_offers_from_last_day):
    """Remove concluded trades from the db"""
    run_query(f"""
        DELETE FROM {BOT_ENV}_trades_history
        WHERE id IN ({", ".join(str(trade['id']) for trade in trade_offers_from_last_day)})
            OR proposal_time > NOW() - INTERVAL 1 DAY
    """)


async def dm_user_about_trade(bot, trade_poster_id: int, matching_trade_poster_id: int, trade: dict):
    trade_poster = await bot.fetch_user(trade_poster_id)
    matching_trade_poster = await bot.fetch_user(matching_trade_poster_id)

    # Send a DM to the trade poster about the matching trade
    await trade_poster.send(embed=trade_dm_embed(trade, matching_trade_poster))
