from discord.ext import commands
from src.commands import lookup


# gets league data based off of discord name (name must be in database)
@commands.command()
async def stats(ctx, search):
    bot = ctx.bot
    
    # query gets league name from database according to discord name input
    query = '''SELECT league_name FROM username_data
               WHERE discord_name=%s '''
    bot.cursor.execute(query, search)
    leagueName = bot.cursor.fetchone()
    leagueName = leagueName.get('league_name')
   
    # calls lookup functions to find summoner information
    await lookup(ctx, search)