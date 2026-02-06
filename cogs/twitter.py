from datetime import datetime
from random import randint
from typing import Self

import aiohttp
import discord
from discord.ext import commands

from constants import TWITTER_CHANNEL_ID, TWITTER_WEBHOOK_URL
import models
from models import FLObjectId, TwitterAccount
from mongo_extended_bot import MongoExtendedBot


FOOTER_ICON = 'https://abs.twimg.com/icons/apple-touch-icon-192x192.png'
DEFAULT_PFP = 'https://upload.wikimedia.org/wikipedia/commons/0/03/Twitter_default_profile_400x400.png'
TWITTER_COLOR = discord.Color.from_rgb(29, 161, 242)


class Twitter(commands.Cog):
    bot: MongoExtendedBot

    def __init__(self: Self, bot: MongoExtendedBot):
        self.bot = bot

    @commands.Cog.listener(name='on_message')
    async def tweet(self: Self, message: discord.Message):
        if (message.author.bot or
            message.channel.id != TWITTER_CHANNEL_ID or
            message.content.startswith(self.bot.command_prefix)):
            return
        
        twitter_account = await self.bot.get_document_by_id(TwitterAccount, FLObjectId(message.author.id))
        if not twitter_account:
            await message.delete(delay=1.0)
            return await message.author.send(f"Your tweet did not send because you "
                                             f"do not have a Twitter account. "
                                             f"You can register an account with "
                                             f"`{self.bot.command_prefix}register [handle]`.")
        if twitter_account.banned:
            await message.delete(delay=1.0)
            return await message.author.send(f"You are banned from Twitter. Your tweet did not send.")
        
        profile_picture = twitter_account.profile_picture if twitter_account.profile_picture else DEFAULT_PFP
        
        embed = discord.Embed(description=message.content, color=TWITTER_COLOR, timestamp=datetime.now())\
                       .set_footer(text='Twitter', icon_url=FOOTER_ICON)\
                       .add_field(name='Likes', value=str(randint(0, 20)))\
                       .add_field(name='Retweets', value=str(randint(0, 30)))\
                       .set_author(name=f"{twitter_account.display_name} (@{twitter_account.handle})",
                                   icon_url=profile_picture)

        attached_file = None
        if message.attachments and message.attachments[0].content_type.startswith("image"):
            attached_file = await message.attachments[0].to_file()
            embed.set_image(url=attached_file.uri) 
        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(TWITTER_WEBHOOK_URL, session=session)
            if attached_file:
                await webhook.send(file=attached_file, embed=embed)
            else:
                await webhook.send(embed=embed)

        # delay to avoid weird client-side ghost messages
        await message.delete(delay=1.0)
        
    @commands.command()
    async def register(self: Self, ctx: commands.Context, *, handle: str):
        if ctx.channel.id != TWITTER_CHANNEL_ID:
            return
        if 3 > len(handle):
            return await ctx.reply("Error: Handle too short (must be at least 3 characters).")
        if 32 < len(handle):
            return await ctx.reply("Error: Handle too long (must be at most 32 characters).")
        if not handle.replace("_", "").isalnum():
            return await ctx.reply("Error: Handle is in an invalid format "
                                   "(must be only alphanumeric or underscores, "
                                   "but not only underscores).")
        
        check_with_user_id = await self.bot.get_document_by_id(TwitterAccount, FLObjectId(ctx.author.id))
        if check_with_user_id and check_with_user_id.banned:
            return await ctx.reply("Error: You are banned from Twitter. You cannot create a new account.")
        if check_with_user_id:
            return await ctx.reply("Error: You already appear to have an account.")
        check_with_handle = await self.bot.get_document(TwitterAccount, {"handle": handle})
        if check_with_handle:
            return await ctx.reply("Error: User already exists with this handle.")
        author_fl_user = await self.bot.get_document_by_id(models.User, FLObjectId(ctx.author.id))
        if not author_fl_user:
            return await ctx.reply(f"Error: You don't seem to be a member."
                                   f"I have no idea how this is possible but contact "
                                   f"Nota for help.")
        
        await self.bot.insert_document(TwitterAccount(
            _id=FLObjectId(ctx.author.id),
            handle=handle,
            display_name=f"{author_fl_user.first_name} {author_fl_user.last_name}"
        ))

        return await ctx.reply(f"Your Twitter account was successfully registered. "
                               f"Your profile picture and display name were automatically "
                               f"set. You can run `{self.bot.command_prefix}displayname` "
                               f"or `{self.bot.command_prefix}pfp` respectively to change them.")
    
    @commands.command()
    async def handle(self: Self, ctx: commands.Context, *, handle: str):
        pass

    @commands.command()
    async def displayname(self: Self, ctx: commands.Context, *, display_name: str):
        pass

    @commands.command()
    async def pfp(self: Self, ctx: commands.Context, *, url: str):
        pass

async def setup(bot: MongoExtendedBot):
    await bot.add_cog(Twitter(bot))
