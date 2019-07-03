from discord.ext import commands
import discord, pymongo, dns, config, asyncio

class inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        wumpdb = pymongo.MongoClient(config.URI)["wumpus-hack"]
        self.users_col = wumpdb['users-beta']


    def calc_loading(self, doc, base):
        load_time = base / ((doc['network']['bandwidth'] * doc['pc']['cpu']) + 1)
        return load_time

    @commands.command(aliases=['i', 'inv'])
    async def inventory(self, ctx):
        if ctx.invoked_subcommand is None:
            if ctx.guild != None:
                await ctx.message.delete()

            #Get user docuemnt from DB and check if they have an account
            doc = self.users_col.find_one({'user_id': str(ctx.author.id)})
            if doc == None:
                await ctx.author.send("`Please type >login to start your adventure!`")
                return

            #Check for online status
            if doc['online'] == False:
                await ctx.author.send("`Your computer is not online. Please >login`")
                return

            else:
                inv_string = "__**Components in Inventory**__\n\n"
                index = 0
                for item in doc['inventory']:
                    inv_string = inv_string + "**%s** - `%s`\n%s GHz | %s MSRP\nID: `%s`\n\n" % (item['type'].upper(), item['name'], str(item['system']), str(item['cost']), str(index))
                    index += 1
                if index == 0:
                    inv_string = inv_string + "```No Items in component Inventory.```"


                embed = discord.Embed(
                    title = "Inventory",
                    description = inv_string,
                    color = 0x7289da
                )
                #Send message
                await ctx.author.send(content="<:done:592819995843624961> `Inventory information retreived`", embed=embed)




def setup(bot):
    bot.add_cog(inventory(bot))
