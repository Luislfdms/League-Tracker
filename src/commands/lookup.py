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

async def process_ranked_data(ctx, summoner_data, q_type):
    # gets players top champion
    champion_data = bot.riot_api.get_champion_mastery.by_summoner(bot.my_region, summoner['id'])  
    topChampID = champion_data[0]['championId']  
    topChamps = bot.champ_dict[str(topChampID)]

    # gathers player stat information q_type determines if it is ranked solo or flex
    rank = summoner_data[q_type]['tier']  
    tier = summoner_data[q_type]['rank']    
    winRate = round(summoner_data[q_type]['wins'] / (summoner_data[q_type]['losses'] + summoner_data[q_type]['wins']), 2)  
    
    # combines rank with tier data and rounds win rate to proper value with 2 decimal places
    rank = rank + ' ' + tier
    winRate = winRate * 100
    winRate = round(winRate, 2)

    await displayRanked(ctx, search, rank, winRate, topChamp, level, summoner_data[q_type]['queueType'])

# looks up league data from username wether typed or aquired from database
@commands.command()
async def lookup(ctx, search):
    bot = ctx.bot
    
    logging.info(f'Looking up {search}')
    discord_name = await process_username(ctx, search)
    logging.info(discord_name)
    
    # gets summoner id by league name then summoner data
    summoner_id_query = "SELECT summoner_id FROM summoner_data WHERE discord_name = %s"
    bot.cursor.execute(summoner_id_query, (discord_name,))
    summoner_id = bot.cursor.fetchone()
    summoner_data = bot.riot_api.get_summoner_stats_by_id(summoner_id)   
    logging.info(summoner_data)
    
    # determines if summoner has ranked data or not
    choice = True
    
    # checks if summoner has ranked data
    if summoner_data[0] != []:
        await process_ranked_data(summoner_data[0], 0)
    if summoner_data[1] != []:
        await process_ranked_data(summoner_data[1], 1)