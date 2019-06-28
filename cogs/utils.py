from discord.ext import commands
import discord

class utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Invite
    @commands.command()
    async def invite(self, ctx):
        #send link to invite the bot to your server
        embed = discord.Embed(
            title = "**Invite Me! 🔗**",
            url = "https://discordapp.com/api/oauth2/authorize?client_id=592803813593841689&permissions=8&scope=self.bot",
            color = 0x7289da
        )
        await ctx.send(embed = embed)

    #Support
    @commands.command()
    async def support(self, ctx):
        #send link to support discord server
        embed = discord.Embed(
            title = "**Support Server! 🔗**",
            url = "https://discord.gg/GC7Pw9Y",
            color = 0x7289da
        )
        await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        #change name on guild join.
        await guild.me.edit(nick="WumpusHack")
        print("WumpusHack Joined "+ str(guild))

    #Github
    @commands.command()
    async def github(self, ctx):
        #send link to github repo
        embed = discord.Embed(
            title = "**Github Repository! 🔗**",
            url = "https://github.com/KAJdev/WumpusHack",
            color = 0x7289da
        )
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(utils(bot))
