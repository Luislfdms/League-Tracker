import discord


# displays ranked information
async def displayRanked(ctx, author, rank, winRate, topChamp, level, rankType):
    
    # gets the profile picture for top champion
    champName = topChamp + ".png"
    champ = discord.File("https://ddragon.leagueoflegends.com/cdn/12.4.1/img/champion/" + champName, filename = champName)
        
    # determines ranked type
    if rankType == 'RANKED_FLEX_5x5':
        title = 'Rank (Ranked Flex)'
    else:
        title = 'Rank (Ranked Solo/Duo)'
    
    # creates embed
    embed = discord.Embed(
        title = title,
        description = rank,
        color = discord.Colour.blurple()
    )
    
    # adds all required information to embed
    embed.set_thumbnail(url = "attachment://" + champName)
    embed.set_author(name = author, icon_url = "attachment://" + champName)
    embed.add_field(name = 'Level', value = level, inline = True)
    embed.add_field(name = 'Win Rate', value = str(winRate) + '%', inline = True)
    embed.add_field(name = 'Top Champions', value = topChamps, inline = True)

    await ctx.send(file = champ, embed = embed)