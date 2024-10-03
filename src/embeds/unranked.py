import discord


# displays unranked information
async def displayUnranked(ctx, author, level):
    logoName = 'funnymonkey.jpeg'
    logo = discord.File("images/" + logoName, filename = logoName)

    embed = discord.Embed(  
        title = 'Level',
        description = level,
        color = discord.Colour.blurple()
    )
    
    embed.set_thumbnail(url = "attachment://" + logoName)
    embed.set_author(name = author)
    embed.add_field(name = 'Info', value = 'No Ranked Data Available', inline = True)

    await ctx.send(file = logo, embed = embed)