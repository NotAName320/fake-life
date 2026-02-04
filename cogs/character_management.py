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
        
        embed = user_info.as_discord_embed()

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

        return await ctx.reply(f"{user_info.first_name} {user_info.last_name} successfully deleted!")


async def setup(bot: MongoExtendedBot):
    await bot.add_cog(CharacterManagement(bot))
