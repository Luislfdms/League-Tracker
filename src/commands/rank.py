import logging
import re
from discord.ext import commands
from src.embeds import displayRanked, displayUnranked

async def process_username(ctx, search) -> str:
    if '@' in search:
        user_id = int(re.sub(r'\D', '', search))
        search = await ctx.bot.fetch_user(user_id)
        return search.name
    
    return search

async def process_ranked_data(ctx, puuid, username, summoner_data):
    bot = ctx.bot
    topChamps = [None, None, None]
    
    # gets players top champion
    champion_data = bot.riot_api.get_summoner_top_champs_by_puuid(puuid)  
    for i in range(0, 3):
        topChampID = champion_data[i]['championId']  
        topChamps[i] = bot.champ_dict[str(topChampID)]
    
    logging.info(topChamps)

    # gathers player stat information q_type determines if it is ranked solo or flex
    rank = summoner_data['tier']  
    tier = summoner_data['rank']    
    winRate = round(summoner_data['wins'] / (summoner_data['losses'] + summoner_data['wins']), 2)  
    
    # combines rank with tier data and rounds win rate to proper value with 2 decimal places
    rank = rank + ' ' + tier
    winRate = winRate * 100
    winRate = round(winRate, 2)

    await displayRanked(ctx, username, rank, winRate, topChamps, summoner_data['queueType'])

# looks up league data from username wether typed or aquired from database
@commands.command()
async def rank(ctx, search):
    bot = ctx.bot
    
    logging.info(f'Looking up {search}')
    discord_name = await process_username(ctx, search)
    logging.info(discord_name)
    
    # Define your SQL queries
    summoner_id_query = "SELECT summoner_id FROM summoner_data WHERE discord_name = %s"
    puuid_query = "SELECT puuid FROM summoner_data WHERE discord_name = %s"

    # Execute the first query to get the summoner_id
    bot.cursor.execute(summoner_id_query, (discord_name,))
    summoner_id = bot.cursor.fetchone()[0]  # Directly fetch the summoner_id
    
    if summoner_id is None:
        await ctx.send('User is not registered.')

    # Execute the second query to get the puuid
    bot.cursor.execute(puuid_query, (discord_name,))
    puuid = bot.cursor.fetchone()[0]  # Directly fetch the puuid

    # Fetch summoner stats using the retrieved summoner_id
    summoner_data = bot.riot_api.get_summoner_stats_by_id(summoner_id)
    if summoner_data is None:
        await ctx.send('Error: Could not fetch summoner data.')
        return
    logging.info(summoner_data)
    
    # checks if summoner has ranked data
    if summoner_data[0] != []:
        await process_ranked_data(ctx, puuid, discord_name, summoner_data[0])
    if summoner_data[1] != []:
        await process_ranked_data(ctx, puuid, discord_name, summoner_data[1])