import discord

from database.guild_settings_manager import save_settings, update_setting, fetch_or_create_settings, DEFAULT_SETTINGS
from utils.general_utils import create_embed, str_and_lower
from utils.types import BaseCommand


class UpdateSetting(BaseCommand):
    async def command_logic(self):
        setting_name = str_and_lower(self.command_params["setting_name"])
        new_value = str_and_lower(self.command_params["new_value"])
        update_setting(self.ctx.guild, setting_name, new_value)
        
        await self.ctx.response.send_message(
            embed=create_embed('Settings have been updated'),
            ephemeral=True
        )


class ShowSettings(BaseCommand):
    def __init__(self, ctx: discord.Interaction, params: dict, guild_settings: dict):
        super().__init__(ctx, params, guild_settings)

    async def command_logic(self):
        settings = fetch_or_create_settings(self.ctx.guild)

        embed = create_embed(title="Server Settings")
        for key, value in settings.items():
            if not key.endswith('_id'):
                embed.add_field(name=key, value=value, inline=False)

        # noinspection PyUnresolvedReferences
        await self.ctx.response.send_message(embed=embed, ephemeral=True)


class ResetSettings(BaseCommand):
    def __init__(self, ctx: discord.Interaction, params: dict, guild_settings: dict):
        super().__init__(ctx, params, guild_settings)

    async def command_logic(self):
        save_settings(self.ctx.guild, **DEFAULT_SETTINGS)
        await self.ctx.response.send_message(
            embed=create_embed('Settings have been reset to default'),
            ephemeral=True
        )
