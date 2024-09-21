import os
import discord
from utils.types import BaseCommand


class TestMessage(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)

    async def command_logic(self):
        # Send a simple message as a response to the interaction
        await self.ctx.response.send_message(f"Hello {self.ctx.user.name}, this is a test message!")


class TestEmbed(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)

    async def command_logic(self):
        # Create an embed object
        embed = discord.Embed(
            title="Test Embed",
            description=f"Hello {self.ctx.user.name}, this is a test embed!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Field 1", value="This is a test field", inline=False)
        embed.set_footer(text="Test footer")

        # Send the embed as a response to the interaction
        await self.ctx.response.send_message(embed=embed)


class TestImage(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)

    async def command_logic(self):
        # Assuming you have an image file in the same directory called "test_image.png"
        image_path = "test_image.png"

        if os.path.exists(image_path):
            # Send the image file as a response to the interaction
            with open(image_path, "rb") as image_file:
                discord_file = discord.File(image_file, filename="test_image.png")
                await self.ctx.response.send_message(file=discord_file)
        else:
            await self.ctx.response.send_message("Image file not found!")
