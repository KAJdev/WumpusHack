import config, discord
from discord.ext import commands

bot = commands.Bot(command_prefix = config.DEFAULT_PREFIX, case_insensitive = True)

initial_extensions = ['cogs.utils',
                      'cogs.main_commands']

for cog in initial_extensions:
    print("loading cog %s..." % cog)
    bot.load_extension(cog)
print("cogs loaded")

@bot.command()
async def reload(ctx, module:str=None):
    if ctx.author.id not in [229695200082132993, 245653078794174465, 282565295351136256]:
        return

    if module in initial_extensions and module != None:
        await ctx.send("reloading cog %s..." % cog)
        bot.reload_extension(module)
        return

    await ctx.send("reloading commands..")
    for cog in initial_extensions:
        print("reloading cog %s..." % cog)
        await ctx.send("reloading cog %s..." % cog)
        bot.reload_extension(cog)

    await ctx.send(content="commands reloaded.")

bot.run(config.TOKEN)
