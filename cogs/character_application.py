from dataclasses import dataclass
from datetime import datetime
from typing import Self

import discord
from discord import ui, ButtonStyle
from discord.ext import commands
from dotenv import load_dotenv

from models import FakeLifeUser, FLObjectId, GeneticStats, pronouns
from mongo_extended_bot import MongoExtendedBot
from utils import getenv_or_exit


load_dotenv()
BOT_OPERATOR_ROLE_NAME = getenv_or_exit("BOT_OPERATOR_ROLE_NAME")
CHARACTER_APPROVALS_CHANNEL = int(getenv_or_exit("CHARACTER_APPROVALS_CHANNEL"))


# select menus
PRONOUN_MENU = [
    discord.SelectOption(label="He/Him", value="He/Him"),
    discord.SelectOption(label="She/Her", value="She/Her"),
    discord.SelectOption(label="They/Them", value="They/Them")
]


@dataclass
class FullApplication:
    user: int
    first_name: str
    last_name: str
    pronouns: str
    genetics: GeneticStats

    @property
    def as_embed(self: Self) -> discord.Embed:
        retval = discord.Embed(colour=0x0, title="New Application", timestamp=datetime.now())
        retval.add_field(name="First Name", value=self.first_name)
        retval.add_field(name="Last Name", value=self.last_name)
        retval.add_field(name="Pronouns", value=self.pronouns, inline=False)
        retval.add_field(name="Physicality", value=self.genetics["physicality"])
        retval.add_field(name="Diligence", value=self.genetics["diligence"])
        retval.add_field(name="Wit", value=self.genetics["wit"])
        retval.add_field(name="Charisma", value=self.genetics["charisma"])
        retval.add_field(name="Luck", value=self.genetics["luck"])

        return retval
    
    @property
    def as_user_document(self: Self) -> FakeLifeUser:
        return FakeLifeUser(
            _id=FLObjectId(str(self.user)),
            first_name=self.first_name,
            last_name=self.last_name,
            pronouns=pronouns.from_string(self.pronouns),
            genetics=self.genetics,

            # defaults
            age=14,
            birthday=1, # TODO: change to current month
            money=20.0,
            gpa=3.0
        )


class ApplicationFormPageOne(ui.Modal, title="Character Application"):
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
            view=GeneticAttributesButton(self)
        )

class ApplicationFormPageTwo(ui.Modal, title="Genetic Attributes"):
    parent: 'ConfirmationButton | GeneticAttributesButton'

    def __init__(self, parent: 'ConfirmationButton | GeneticAttributesButton') -> None:
        self.parent = parent
        super().__init__(timeout=None)
    
    physicality = ui.Label(text="Physicality", component=ui.TextInput(placeholder="0-10", min_length=1, max_length=2))
    diligence = ui.Label(text="Diligence", component=ui.TextInput(placeholder="0-10", min_length=1, max_length=2))
    wit = ui.Label(text="Wit", component=ui.TextInput(placeholder="0-10", min_length=1, max_length=2))
    charisma = ui.Label(text="Charisma", component=ui.TextInput(placeholder="0-10", min_length=1, max_length=2))
    luck = ui.Label(text="Luck", component=ui.TextInput(placeholder="0-10", min_length=1, max_length=2))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            physicality, diligence, wit, charisma, luck = (
                int(x.component.value) for x in (self.physicality, self.diligence, self.wit, self.charisma, self.luck) # type: ignore
            ) 
        except ValueError:
            await interaction.response.send_message("One or more fields was not a valid number. Please try again.", ephemeral=True)
            return
        
        if any((x > 10 or x < 1 for x in (physicality, diligence, wit, charisma, luck))):
            await interaction.response.send_message("One or more fields was out of range. Please try again.", ephemeral=True)
            return
        sum_of_stats = sum((physicality, diligence, wit, charisma, luck))
        if sum_of_stats > 27:
            await interaction.response.send_message("One or more fields was out of range. Please try again.", ephemeral=True)
            return
        sum_is_under_warning = f'**WARNING:** Sum of genetic stats is under 27! You have {27 - sum_of_stats} points unused.\n' if sum_of_stats < 27 else ""


        self.parent.exhausted = True
        await interaction.response.send_message(f"Genetic information submitted! To review:\n\n"
            f"Physicality: {physicality}\n"
            f"Dilgence: {diligence}\n"
            f"Wit: {wit}\n"
            f"Charisma: {charisma}\n"
            f"Luck: {luck}\n"
            f"{sum_is_under_warning}\n"
            f"To **confirm and submit for approval**, please press the green button below.\n"
            f"To **re-enter**, please press the red button.", ephemeral=True, view=ConfirmationButton(self.parent.page_one, self))


class StartApplicationButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Start Application", style=ButtonStyle.green, custom_id="fake_life_bot:StartApplicationButton:start_application")
    async def start_application(self, interaction: discord.Interaction, button: ui.Button):
        assert interaction.guild is not None
        member_role = discord.utils.get(interaction.guild.roles, name="Member")
        assert member_role is not None and isinstance(interaction.user, discord.Member)

        if member_role in interaction.user.roles:
            return await interaction.response.send_message("You already have a character! "
                                                           "If you would like a new character, "
                                                           "please ask admin to delete your "
                                                           "current character.", ephemeral=True)
        return await interaction.response.send_modal(ApplicationFormPageOne())


class GeneticAttributesButton(ui.View):
    page_one: ApplicationFormPageOne
    exhausted: bool = False
    def __init__(self, page_one: ApplicationFormPageOne):
        self.page_one = page_one
        super().__init__(timeout=None)

    @ui.button(label="Pick Genetic Attributes", style=ButtonStyle.green)
    async def start_application(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        return await interaction.response.send_modal(ApplicationFormPageTwo(self))
    
    @ui.button(label="Re-enter Personal Information", style=ButtonStyle.red)
    async def redo_part_one(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True
        return await interaction.response.send_modal(ApplicationFormPageOne())


class ConfirmationButton(ui.View):
    page_one: ApplicationFormPageOne
    page_two: ApplicationFormPageTwo
    exhausted: bool = False
    def __init__(self, page_one: ApplicationFormPageOne, page_two: ApplicationFormPageTwo):
        self.page_one = page_one
        self.page_two = page_two
        super().__init__(timeout=None)

    @ui.button(label="Confirm and Submit", style=ButtonStyle.green)
    async def confirm_and_submit(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True
        await interaction.response.send_message("Submitted! Please wait for admin approval.", ephemeral=True)

        full_application = FullApplication(
            user=interaction.user.id,
            first_name=self.page_one.first_name.component.value, # type: ignore
            last_name=self.page_one.last_name.component.value, # type: ignore
            pronouns=self.page_one.pronouns.component.value, # type: ignore
            genetics=GeneticStats(
                self.page_two.physicality.component.value, # type: ignore
                self.page_two.diligence.component.value, # type: ignore
                self.page_two.wit.component.value, # type: ignore
                self.page_two.charisma.component.value, # type: ignore
                self.page_two.luck.component.value # type: ignore
            )
        )
        
        assert interaction.guild is not None
        approvals_channel = interaction.guild.get_channel(CHARACTER_APPROVALS_CHANNEL)
        bot_operator_role = discord.utils.get(interaction.guild.roles, name=BOT_OPERATOR_ROLE_NAME)

        assert isinstance(approvals_channel, discord.TextChannel) and bot_operator_role is not None
        return await approvals_channel.send(f"{bot_operator_role.mention} New application submitted!",
                                            embed=full_application.as_embed,
                                            view=ApprovalButtons(full_application))
    
    @ui.button(label="Re-enter Genetic Information", style=ButtonStyle.red)
    async def redo_part_one(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        return await interaction.response.send_modal(ApplicationFormPageTwo(self))


class ApprovalButtons(ui.View):
    application: FullApplication
    exhausted: bool

    def __init__(self, application: FullApplication):
        self.application = application
        super().__init__(timeout=None)

    @ui.button(style=ButtonStyle.green, emoji="✅")
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True

        original_user = interaction.client.get_user(self.application.user)
        if not original_user:
            return await interaction.response.send_message("Applying user seems to have left.")
        welcome_channel = discord.utils.get(interaction.guild.channels, name="welcome") # type: ignore
        assert welcome_channel is not None
        await original_user.send(f"Congrats, {self.application.first_name}! Your Fake Life application "
                                 f"has been accepted! You start as a 14 year old in high school with a "
                                 f"3.0 GPA and $20 (which will be granted monthly as an allowance). "
                                 f"Please refer to the pinned document in {welcome_channel.mention} "
                                 f"for info on how to play.")

        assert isinstance(interaction.client, MongoExtendedBot)
        await interaction.client.insert_document(self.application.as_user_document)

        return await interaction.response.send_message("Appplication accepted and inserted into database!")
    
    @ui.button(style=ButtonStyle.red, emoji="❌")
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        if self.exhausted:
            return await interaction.response.send_message("Choice already made!", ephemeral=True)
        self.exhausted = True

        original_user = interaction.client.get_user(self.application.user)
        if original_user:
            await original_user.send("Unfortunately, your Fake Life application was rejected. "
                                     "Please contact an admin for more info, and reapply "
                                     "if you want to.")

        return await interaction.response.send_message("Application rejected!")


class CharacterApplication(commands.Cog):
    bot: commands.Bot

    def __init__(self: Self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener(name="on_ready")
    async def register_views(self: Self):
        self.bot.add_view(StartApplicationButton())

    @commands.command(name='cca')
    @commands.has_role(BOT_OPERATOR_ROLE_NAME)
    async def create_character_application(self: Self, ctx: commands.Context):
        await ctx.message.delete()
        return await ctx.channel.send("Click this to start your application!", view=StartApplicationButton())


async def setup(bot: commands.Bot):
    await bot.add_cog(CharacterApplication(bot))
