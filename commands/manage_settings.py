from database.guild_settings_manager import save_settings, update_setting, fetch_or_create_settings, DEFAULT_SETTINGS
from embeds.embeds import create_embed, show_settings_embed
from utils.general_utils import str_and_lower
from utils.types import BaseCommand


class UpdateSetting(BaseCommand):
    async def command_logic(self):
        setting_name = str_and_lower(self.command_params["setting_name"])
        new_value = str_and_lower(self.command_params["new_value"])
        update_setting(self.ctx.guild, setting_name, new_value)

        await self.ctx.response.send_message(
            embed=create_embed("Setting Updated Successfully", f"'{setting_name}' has been updated to '{new_value}'"),
            ephemeral=True
        )


class ShowSettings(BaseCommand):
    async def command_logic(self):
        settings = fetch_or_create_settings(self.ctx.guild)
        await self.ctx.response.send_message(embed=show_settings_embed(settings), ephemeral=True)


class ResetSettings(BaseCommand):
    async def command_logic(self):
        save_settings(self.ctx.guild, **DEFAULT_SETTINGS)
        await self.ctx.response.send_message(
            embed=create_embed("Settings have been reset to default", "Use `/show_settings` to see them."),
            ephemeral=True
        )
