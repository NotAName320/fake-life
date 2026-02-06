from typing import Union

import discord
from discord import ui

from models import GeneticStats
from . import confirmation_button
from . import genetic_attributes_button


PageTwoParent = Union['confirmation_button.ConfirmationButton', 'genetic_attributes_button.GeneticAttributesButton']


class PageTwo(ui.Modal, title="Genetic Attributes"):
    parent: PageTwoParent

    def __init__(self, parent: PageTwoParent) -> None:
        self.parent = parent
        super().__init__(timeout=None)
    
    physicality = ui.Label(text="Physicality", component=ui.TextInput(placeholder="1-10", min_length=1, max_length=2))
    diligence = ui.Label(text="Diligence", component=ui.TextInput(placeholder="1-10", min_length=1, max_length=2))
    wit = ui.Label(text="Wit", component=ui.TextInput(placeholder="1-10", min_length=1, max_length=2))
    charisma = ui.Label(text="Charisma", component=ui.TextInput(placeholder="1-10", min_length=1, max_length=2))
    luck = ui.Label(text="Luck", component=ui.TextInput(placeholder="1-10", min_length=1, max_length=2))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            physicality, diligence, wit, charisma, luck = (
                int(x.component.value) for x in (self.physicality, self.diligence, self.wit, self.charisma, self.luck)
            ) 
        except ValueError:
            await interaction.response.send_message("One or more fields was not a valid number. Please try again.", ephemeral=True)
            return
        
        if any((x > 10 or x < 1 for x in (physicality, diligence, wit, charisma, luck))):
            await interaction.response.send_message("One or more fields was out of range. Please try again.", ephemeral=True)
            return
        sum_of_stats = sum((physicality, diligence, wit, charisma, luck))
        if sum_of_stats > 28:
            await interaction.response.send_message("One or more fields was out of range. Please try again.", ephemeral=True)
            return
        sum_is_under_warning = f'**WARNING:** Sum of genetic stats is under 28! You have {28 - sum_of_stats} points unused.\n' if sum_of_stats < 28 else ""

        self.parent.exhausted = True
        self.parent.in_progress_application.genetics = GeneticStats(
            physicality=physicality,
            diligence=diligence,
            wit=wit,
            charisma=charisma,
            luck=luck
        )
        await interaction.response.send_message(f"Genetic information submitted! To review:\n\n"
            f"Physicality: {physicality}\n"
            f"Diligence: {diligence}\n"
            f"Wit: {wit}\n"
            f"Charisma: {charisma}\n"
            f"Luck: {luck}\n"
            f"{sum_is_under_warning}\n"
            f"To **confirm and submit for approval**, please press the green button below.\n"
            f"To **re-enter**, please press the red button.", ephemeral=True,
            view=confirmation_button.ConfirmationButton(self.parent.in_progress_application))
