import discord


async def displayLeaderboard(ctx, names):
    bot = ctx.bot
    
    embed = discord.Embed(
        title = 'Leaderboard',
        color = discord.Colour.blurple()
    )

    for i in names:
        summoner = bot.watcher.summoner.by_name(bot.my_region, i['league_name'])  
        summoner_data = bot.watcher.league.by_summoner(bot.my_region, summoner['id'])      

        level = summoner['summonerLevel']  
        choice = 1
        
        try:
            summoner_data[0]  
        except IndexError:
            choice = 0
            
        if choice == 1:
            champion_data = bot.watcher.champion_mastery.by_summoner(bot.my_region, summoner['id'])  
            topChampID = champion_data[0]['championId']  
            latest = bot.watcher.data_dragon.versions_for_region(bot.my_region)['n']['champion']  
            static_champ_list = bot.watcher.data_dragon.champions(latest, False, 'en_US')
            champ_dict = {}

            for key in static_champ_list['data']:  
                row = static_champ_list['data'][key]  
                champ_dict[row['key']] = row['id']
            print(summoner_data[0]['queueType'])  
            if summoner_data[0]['queueType'] != 'RANKED_SOLO_5x5':   
                rank = summoner_data[1]['tier']    
                tier = summoner_data[1]['rank']    
                winRate = round(summoner_data[1]['wins'] / (summoner_data[1]['losses'] + summoner_data[1]['wins']), 2)  
            else:
                rank = summoner_data[0]['tier']  
                tier = summoner_data[0]['rank']    #type: ignore
                winRate = round(summoner_data[0]['wins'] / (summoner_data[0]['losses'] + summoner_data[0]['wins']), 2)  
        
            rank = rank + ' ' + tier
            topChamp = champ_dict[str(topChampID)]
            winRate = winRate * 100
            winRate = round(winRate, 2)

            s = "Square.png"
            champName = topChamp + s

            champ = discord.File("/home/ubuntu/Version 2.0/Champion Pictures/" 
            + champName, filename = champName)
            if i['league_name'] == 'TossTheNoodles':
                rank = 'IRON IV'

            embed.add_field(name = 'Name:', value = i['league_name'] + '    -    ' + rank + '    -    ' + str(winRate) + '%', inline = False)
        else:
    
            if i['league_name'] == 'gatoralanw':
                logoName = 'ucflol.png'
            else:
                logoName = 'funnymonkey.jpeg'
            logo = discord.File("/home/ubuntu/Version 2.0/Champion Pictures/" 
            + logoName, filename = logoName)

            embed.add_field(name = 'Name:', value = i['league_name'] + '    -    ' + str(level) + '    -    ' + 'Unranked', inline = False)
    await ctx.send(embed = embed)