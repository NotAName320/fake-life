# select menu
import discord
from discord import ui

from models import CharacterApplication
from .genetic_attributes_button import GeneticAttributesButton


PRONOUN_MENU = [
    discord.SelectOption(label="He/Him", value="He/Him"),
    discord.SelectOption(label="She/Her", value="She/Her"),
    discord.SelectOption(label="They/Them", value="They/Them")
]


class PageOne(ui.Modal, title="Character Application"):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    header = ui.TextDisplay("Personal Information")
    # name
    first_name = ui.Label(text='First Name', component=ui.TextInput())
    last_name = ui.Label(text="Last Name", component=ui.TextInput())

    # woke
    pronouns = ui.Label(text="Pronouns", component=ui.Select(options=PRONOUN_MENU))

    async def on_submit(self, interaction: discord.Interaction):
        full_name = f'{self.first_name.component.value} {self.last_name.component.value}' # type: ignore
        pronouns = self.pronouns.component.values[0] # type: ignore
        await interaction.response.send_message(
            f"Personal information submitted! To review:\n\n"
            f"Name: {full_name}\n"
            f"Pronouns: {pronouns}\n\n"
            f"To **proceed**, please press the green button below.\n"
            f"To **start over**, please press the red button.",  
            ephemeral=True,
            view=GeneticAttributesButton(CharacterApplication(
                user=interaction.user,
                first_name=self.first_name.component.value,
                last_name=self.last_name.component.value,
                pronouns=pronouns
            ))
        )