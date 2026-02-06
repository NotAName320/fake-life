import discord
from discord import ButtonStyle, ui

from . import page_one
from views.view_base import FakeLifeView


class StartApplicationButton(FakeLifeView):
    @ui.button(label="Start Application", style=ButtonStyle.green, custom_id="fake_life_bot:StartApplicationButton:start_application")
    async def start_application(self, interaction: discord.Interaction, button: ui.Button):
        member_role = discord.utils.get(interaction.guild.roles, name="Member")

        if member_role in interaction.user.roles:
            return await interaction.response.send_message("You already have a character! "
                                                           "If you would like a new character, "
                                                           "please ask admin to delete your "
                                                           "current character.", ephemeral=True)
        return await interaction.response.send_modal(page_one.PageOne())
