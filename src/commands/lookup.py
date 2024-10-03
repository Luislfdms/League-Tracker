from discord.ext import commands
from src.embeds import displayRanked, displayUnranked


# looks up league data from username wether typed or aquired from database
@commands.command()
async def lookup(ctx, search):
    bot = ctx.bot
    
    # gets summoner id by league name then summoner data
    summoner = bot.watcher.summoner.by_name(bot.my_region, search)    
    summoner_data = bot.watcher.league.by_summoner(bot.my_region, summoner['id'])      
    
    # determines if summoner has ranked data or not
    choice = True
    
    # league level
    level = summoner['summonerLevel']  
    
    try:
        summoner_data[0]
    except:
        choice = False
        
    # if player is ranked displays name, rank, winRate, topChamp, and level
    if choice:
    
        # gets players top champion
        champion_data = bot.watcher.champion_mastery.by_summoner(bot.my_region, summoner['id'])  
        topChampID = champion_data[0]['championId']  
        topChamp = bot.champ_dict[str(topChampID)]
        
        # by default looks for players ranked solo information
        q_type = 1
        rankType = 'RANKED_SOLO_5x5'
        
        # if player has does not have ranked solo information available returns ranked flex information
        if summoner_data[0]['queueType'] != 'RANKED_SOLO_5x5':   
            q_type = 0
            rankType = 'RANKED_FLEX_5x5'

        # gathers player stat information q_type determines if it is ranked solo or flex
        rank = summoner_data[q_type]['tier']  
        tier = summoner_data[q_type]['rank']    
        winRate = round(summoner_data[q_type]['wins'] / (summoner_data[q_type]['losses'] + summoner_data[q_type]['wins']), 2)  
        
        # combines rank with tier data and rounds win rate to proper value with 2 decimal places
        rank = rank + ' ' + tier
        winRate = winRate * 100
        winRate = round(winRate, 2)

        await displayRanked(ctx, search, rank, winRate, topChamp, level, rankType)
    else:
        await displayUnranked(ctx, search, level)