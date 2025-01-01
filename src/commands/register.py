from discord.ext import commands
import logging

# Adds user's League username (summoner_id) to the database
@commands.command()
async def register(ctx, riot_id):
    bot = ctx.bot
    author = ctx.message.author.name

    # Check if the user is already registered
    bot.cursor.execute('SELECT COUNT(*) FROM summoner_data WHERE discord_name = %s', (author,))
    result = bot.cursor.fetchone()

    if result[0] > 0:
        # User already exists
        await ctx.send(f'{author}, you are already registered!')
    elif '#' not in riot_id:    
        await ctx.send('Invalid Riot ID. Please include the tagline #.')
    else:
        summoner_name, tagline = riot_id.split('#')
        logging.info(f'{summoner_name} {tagline}')
        response = bot.riot_api.get_puuid_by_riotid_name(summoner_name, tagline)
        if response is None:
            logging.error('Error: Invalid Riot ID')
            await ctx.send('Invalid Riot ID. Please try again.')
        else:
            logging.info(response)
            summoner_id = bot.riot_api.get_summoner_by_puuid(response['puuid'])["id"]
            # Insert the user into the database
            bot.cursor.execute('''
                INSERT INTO summoner_data (discord_name, riot_id, summoner_id, puuid) 
                VALUES (%s, %s, %s, %s)
            ''', (author, riot_id, summoner_id, response['puuid'])) 
            bot.sql_connection.commit()  
            await ctx.send('Registration successful!')