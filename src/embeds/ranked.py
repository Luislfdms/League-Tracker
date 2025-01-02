import discord
import aiohttp
import io

# displays ranked information
async def displayRanked(ctx, player, rank, winRate, topChamps, rankType):
    
    # Construct the champion image URL
    champ_name = topChamps[0] + ".png"
    champ_url = f"https://ddragon.leagueoflegends.com/cdn/12.4.1/img/champion/{champ_name}"
    
    # Fetch the champion image
    async with aiohttp.ClientSession() as session:
        async with session.get(champ_url) as response:
            if response.status != 200:
                await ctx.send("Could not fetch champion image.")
                return
            image_data = await response.read()
    
    # Create a file-like object from the image data
    image_file = io.BytesIO(image_data)
    discord_file = discord.File(fp=image_file, filename=champ_name)
        
    # determines ranked type
    if rankType == 'RANKED_FLEX_SR':
        title = 'Ranked Flex'
    else:
        title = 'Ranked Solo/Duo'
    
    # creates embed
    embed = discord.Embed(
        title = title,
        description = rank,
        color = discord.Colour.blurple()
    )
    
    # adds all required information to embed
    embed.set_thumbnail(url = "attachment://" + champ_name)
    embed.set_author(name = player, icon_url = "attachment://" + champ_name)
    embed.add_field(name = 'Win Rate', value = str(winRate) + '%', inline = True)
    embed.add_field(name = 'Top Champions', value = topChamps, inline = True)

    await ctx.send(file = discord_file, embed = embed)