import discord
from discord import ButtonStyle, ui

from models import CharacterApplication
from views import FakeLifeView
from . import page_one
from . import page_two


class GeneticAttributesButton(FakeLifeView):
    in_progress_application: CharacterApplication
    exhausted: bool = False
    def __init__(self, in_progress_application: CharacterApplication):
        self.in_progress_application = in_progress_application
        super().__init__()

    @ui.button(label="Pick Genetic Attributes", style=ButtonStyle.green)
    async def start_application(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        return await interaction.response.send_modal(page_two.PageTwo(self))
    
    @ui.button(label="Re-enter Personal Information", style=ButtonStyle.red)
    async def redo_part_one(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True
        return await interaction.response.send_modal(page_one.PageOne())
