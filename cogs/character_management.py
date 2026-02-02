from typing import Self, Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context

from constants import BOT_OPERATOR_ROLE_NAME, MEMBER_ROLE_NAME
import models
from models import FLObjectId
from mongo_extended_bot import MongoExtendedBot


class CharacterManagement(commands.Cog):
    bot: MongoExtendedBot

    def __init__(self, bot: MongoExtendedBot):
        self.bot = bot

    @commands.command(name='info')
    async def user_info(self: Self, ctx: Context, user: Optional[discord.Member] = None):
        if not user:
            user = ctx.author
        
        user_info = await self.bot.get_document(models.User, {'_id': FLObjectId(user.id)})
        if user_info is None:
            return await ctx.reply("User not found.")
        
        embed = discord.Embed(colour=0x0, title="Character Info")\
                       .add_field(name="Name", value=f"{user_info["first_name"]} {user_info["last_name"]}")\
                       .add_field(name="Age", value=user_info['age'])\
                       .add_field(name="Pronouns", value=f"{user_info['pronouns']["they"]}/{user_info['pronouns']["them"]}")\
                       .add_field(name="Birthday", value=f'{await self.bot.calculate_birthday(user_info)}')\
                       .add_field(name="Net Worth", value=f'${user_info['money']:.2f}')\
                       .add_field(name="Relationship Status", value=f"With {user_info['relationship']}"
                                  if user_info['relationship'] else "Single")\
                       .add_field(name="Education", value=f'{user_info["education"]}')\
                       .add_field(name="Job", value=f"{user_info['job']}")\
                       .add_field(name="Traits", value=user_info["traits"] if user_info["traits"] else "None")\
                       .add_field(name="Genetic Attributes",
                                  value=f'```Physicality: {user_info["genetics"]["physicality"]}\n'
                                        f'Diligence: {user_info["genetics"]["diligence"]}\n'
                                        f'Wit: {user_info["genetics"]["wit"]}\n'
                                        f'Charisma: {user_info["genetics"]["charisma"]}\n'
                                        f'Luck: {user_info["genetics"]["luck"]}```',
                                  inline=False)

        await ctx.reply(embed=embed)

    @commands.command(name="deluser")
    @commands.has_role(BOT_OPERATOR_ROLE_NAME)
    async def delete_user(self: Self, ctx: Context, user: discord.Member):
        user_info = await self.bot.get_document(models.User, {'_id': FLObjectId(user.id)})
        if user_info is None:
            return await ctx.reply("User not found.")

        await self.bot.delete_document(models.User, {'_id': FLObjectId(user.id)})

        member_role = discord.utils.get(ctx.guild.roles, name=MEMBER_ROLE_NAME)
        await user.remove_roles(member_role)

        return await ctx.reply(f"{user_info['first_name']} {user_info['last_name']} successfully deleted!")


async def setup(bot: MongoExtendedBot):
    await bot.add_cog(CharacterManagement(bot))
