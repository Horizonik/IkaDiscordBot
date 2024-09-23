import discord

from utils.constants import SETTINGS_FILE_PATH
from utils.general_utils import create_embed
from utils.settings_manager import DEFAULT_SETTINGS, save_settings, get_region_id, get_world_id, REGION_MAPPINGS, WORLD_MAPPINGS
from utils.types import BaseCommand


class ChangeSetting(BaseCommand):
    def __init__(self, ctx: discord.Interaction, params: dict, server_settings: dict):
        super().__init__(ctx, params, server_settings)

    async def command_logic(self):
        guild_id = str(self.ctx.guild.id)
        setting_name = str(self.command_params["setting_name"]).lower()
        new_value = str(self.command_params["new_value"]).lower()

        if setting_name not in DEFAULT_SETTINGS:
            await self.ctx.response.send_message(
                embed=create_embed(
                    f"'{setting_name}' key doesn't exist in the settings",
                    "You can only set existing keys!",
                    discord.Color.red()
                ),
                ephemeral=True
            )
            return

        if setting_name == "region":
            await self.change_region_setting(new_value, guild_id)

        elif setting_name == "world":
            await self.change_world_setting(new_value, guild_id)

        else:
            self.servers_settings[guild_id][setting_name] = new_value

        save_settings(self.servers_settings, SETTINGS_FILE_PATH)
        await self.ctx.response.send_message(
            embed=create_embed(f'Setting `{setting_name}` has been updated to `{new_value}`.'),
            ephemeral=True
        )

    async def change_region_setting(self, new_value: str, guild_id):
        try:
            region_id = get_region_id(new_value, REGION_MAPPINGS)
            self.servers_settings[guild_id]['region_id'] = region_id
            self.servers_settings[guild_id]['region'] = new_value

        except ValueError as e:
            await self.ctx.response.send_message(
                embed=create_embed(str(e), color=discord.Color.red()),
                ephemeral=True
            )

    async def change_world_setting(self, new_value: str, guild_id):
        try:
            world_id = get_world_id(new_value, WORLD_MAPPINGS)
            self.servers_settings[guild_id]['world_id'] = world_id
            self.servers_settings[guild_id]['world'] = new_value

        except ValueError as e:
            await self.ctx.response.send_message(
                embed=create_embed(str(e), color=discord.Color.red()),
                ephemeral=True
            )


class ShowSettings(BaseCommand):
    def __init__(self, ctx: discord.Interaction, params: dict, server_settings: dict):
        super().__init__(ctx, params, server_settings)

    async def command_logic(self):
        guild_id = str(self.ctx.guild.id)
        settings = self.servers_settings.get(guild_id, DEFAULT_SETTINGS)

        embed = create_embed(title="Server Settings")
        for key, value in settings.items():
            if not key.endswith('_id'):
                embed.add_field(name=key, value=value, inline=False)

        await self.ctx.response.send_message(embed=embed, ephemeral=True)


class ResetSettings(BaseCommand):
    def __init__(self, ctx: discord.Interaction, params: dict, server_settings: dict):
        super().__init__(ctx, params, server_settings)

    async def command_logic(self):
        guild_id = str(self.ctx.guild.id)
        self.servers_settings[guild_id] = DEFAULT_SETTINGS.copy()

        save_settings(self.servers_settings, SETTINGS_FILE_PATH)
        await self.ctx.response.send_message(
            embed=create_embed(f'Settings have been reset to default'),
            ephemeral=True
        )
