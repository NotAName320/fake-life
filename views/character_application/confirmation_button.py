import discord
from discord import ButtonStyle, ui

from constants import BOT_OPERATOR_ROLE_NAME, CHARACTER_APPROVALS_CHANNEL_ID
from models import CharacterApplication
from views import FakeLifeView
from .approval_buttons import ApprovalButtons
from . import page_two


class ConfirmationButton(FakeLifeView):
    in_progress_application: CharacterApplication
    exhausted: bool = False
    def __init__(self, in_progress_application: CharacterApplication):
        self.in_progress_application = in_progress_application
        super().__init__()

    @ui.button(label="Confirm and Submit", style=ButtonStyle.green)
    async def confirm_and_submit(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True
        await interaction.response.send_message("Submitted! Please wait for admin approval.", ephemeral=True)

        approvals_channel = interaction.guild.get_channel(CHARACTER_APPROVALS_CHANNEL_ID)
        bot_operator_role = discord.utils.get(interaction.guild.roles, name=BOT_OPERATOR_ROLE_NAME)

        return await approvals_channel.send(f"{bot_operator_role.mention} New application submitted!",
                                            embed=self.in_progress_application.as_embed,
                                            view=ApprovalButtons(self.in_progress_application))
    
    @ui.button(label="Re-enter Genetic Information", style=ButtonStyle.red)
    async def redo_part_one(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        return await interaction.response.send_modal(page_two.PageTwo(self))
