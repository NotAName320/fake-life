import traceback
import discord
from discord import ui


class FakeLifeView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        unwrapped_error: Exception = getattr(error, 'original', error)
        formatted_error = "".join(traceback.format_exception(type(unwrapped_error), unwrapped_error, tb=unwrapped_error.__traceback__))

        errordesc = f'```py\n{formatted_error}\n```'
        embed = discord.Embed(title='Error', description=errordesc, color=0)
        app_info = await interaction.client.application_info()
        embed.set_footer(text=f'Please contact {app_info.owner} for help.')
        await interaction.response.send_message(embed=embed)

        return await super().on_error(interaction, error, item)
