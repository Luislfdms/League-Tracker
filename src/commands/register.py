from discord.ext import commands


# adds users league username to database
@commands.command()
async def register(ctx, arg):
    bot = ctx.bot
    
    author = ctx.message.author.name
    # query call to mySql database to 
    bot.cursor.execute('''
        INSERT INTO username_data (discord_name, league_name) VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE league_name=%s
        ''', (author, arg, arg))
    bot.sql_connection.commit()
    
    await ctx.send('Registration succesful!')