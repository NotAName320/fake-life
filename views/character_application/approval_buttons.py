import discord
from discord import ButtonStyle, ui

from constants import MEMBER_ROLE_NAME
from models.character_application import CharacterApplication
from views.view_base import FakeLifeView


class ApprovalButtons(FakeLifeView):
    application: CharacterApplication
    exhausted: bool = False

    def __init__(self, application: CharacterApplication):
        self.application = application
        super().__init__()

    @ui.button(style=ButtonStyle.green, emoji="✅")
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True

        original_user = interaction.guild.get_member(self.application.user.id)
        if not original_user:
            return await interaction.response.send_message("Applying user seems to have left.")
        welcome_channel = discord.utils.get(interaction.guild.channels, name="welcome")
        await original_user.send(f"Congrats, {self.application.first_name}! Your Fake Life application "
                                 f"has been accepted! You start as a 14 year old in high school with a "
                                 f"3.0 GPA and $20 (which will be granted monthly as an allowance). "
                                 f"Please refer to the pinned document in {welcome_channel.mention} "
                                 f"for info on how to play.")
        
        member_role = discord.utils.get(interaction.guild.roles, name=MEMBER_ROLE_NAME)
        await original_user.add_roles(member_role)

        await interaction.client.insert_document(self.application.as_user_document(await interaction.client.get_current_date()))

        return await interaction.response.send_message("Appplication accepted and inserted into database!")
    
    @ui.button(style=ButtonStyle.blurple, emoji="❌")
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True

        original_user = interaction.guild.get_member(self.application.user.id)
        if original_user:
            await original_user.send("Unfortunately, your Fake Life application was rejected. "
                                     "Please contact an admin for more info, and reapply "
                                     "if you want to.")

        return await interaction.response.send_message("Application rejected!")
