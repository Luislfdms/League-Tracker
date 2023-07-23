# LeagueTracker.py
# Luis Souto
# Version 2.0
# 2022

# imported libraries
import discord
from discord import guild, member, user
from discord.ext.commands import bot
from discord.ext.commands.converter import MemberConverter
from discord import message
from dotenv import load_dotenv
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
import os
import pymysql
import pymysql.cursors
from asyncio import events
import pandas as pd
import time

# discord bot token(for connecting to bot)
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_TOKEN = os.getenv('RIOT_TOKEN')
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(intents = intents, command_prefix = '-')

# accessing riot games API
watcher = LolWatcher('RGAPI-681e42f3-4703-4f39-bd91-08381faf0a1d')
my_region = 'na1'

# connect to mysql database
sql_connection = pymysql.connect(
    host='league-tracker-database.cwn2oakyjrry.us-east-1.rds.amazonaws.com',
    user='admin',
    password='Saberlfdms1',
    database='league_tracker',
    cursorclass=pymysql.cursors.DictCursor
)

# setup cursor for executing database queries
cursor = sql_connection.cursor()
cursor.execute("USE league_tracker")
sql_connection.commit()

# creates list of champions information
latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']  # type: ignore
static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')

# takes champion information and filters out till only champion names left
champ_dict = {}
for key in static_champ_list['data']:  # type: ignore
    row = static_champ_list['data'][key]  # type: ignore
    champ_dict[row['key']] = row['id']

# bot is connected to server
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

# adds users league username to database
@client.command()
async def setup(ctx, arg):
    author = ctx.message.author.name
    # query call to mySql database to 
    cursor.execute('''
        INSERT INTO username_data (discord_name, league_name) VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE league_name=%s
        ''', (author, arg, arg))
    sql_connection.commit()
    await ctx.send('Setup succesful!')

# gets league data based off of discord name (name must be in database)
@client.command()
async def stats(ctx, search):
    # query gets league name from database according to discord name input
    query = '''SELECT league_name FROM username_data
               WHERE discord_name=%s '''
    cursor.execute(query, search)
    leagueName = cursor.fetchone()
    leagueName = leagueName.get('league_name')
   
    # calls lookup functions to find summoner information
    await lookup(ctx, search)
    
# looks up league data from username wether typed or aquired from database
@client.command()
async def lookup(ctx, search):
    
    rankType = ''
    # gets summoner id by league name then summoner data
    summoner = watcher.summoner.by_name(my_region, search)    # type: ignore
    summoner_data = watcher.league.by_summoner(my_region, summoner['id'])      # type: ignore
    
    # 1 if account is ranked and 0 if unranked
    choice = 1
    
    # league level
    level = summoner['summonerLevel']  # type: ignore
    
    # checks if player is ranked returs choice 0 if not
    try:
        summoner_data[0]  # type: ignore
    except IndexError:
        choice = 0
        
    # if player is ranked displays name, rank, winRate, topChamp, and level
    if choice == 1:
    
        # gets players top champion
        champion_data = watcher.champion_mastery.by_summoner(my_region, summoner['id'])  # type: ignore
        topChampID = champion_data[0]['championId']  # type: ignore
        topChamp = champ_dict[str(topChampID)]
        
        # if player has does not have ranked solo information available returns ranked flex information
        if summoner_data[0]['queueType'] != 'RANKED_SOLO_5x5' and summoner_data[1] == None:   # type: ignore
            rank = summoner_data[0]['tier']    # type: ignore
            tier = summoner_data[0]['rank']    # type: ignore
            winRate = round(summoner_data[0]['wins'] / (summoner_data[0]['losses'] + summoner_data[0]['wins']), 2)  # type: ignore
            rankType = 'RANKED_FLEX_5x5'
        elif summoner_data[0]['queueType'] != 'RANKED_SOLO_5x5':  # type: ignore
            rank = summoner_data[1]['tier']    # type: ignore
            tier = summoner_data[1]['rank']    # type: ignore
            winRate = round(summoner_data[1]['wins'] / (summoner_data[1]['losses'] + summoner_data[1]['wins']), 2)  # type: ignore
            rankType = 'RANKED_SOLO_5x5'
        else:
            print('here')
            rank = summoner_data[0]['tier']  # type: ignore
            tier = summoner_data[0]['rank']    #type: ignore
            winRate = round(summoner_data[0]['wins'] /  # type: ignore
            (summoner_data[0]['losses'] + summoner_data[0]['wins']), 2)  # type: ignore
            rankType = 'RANKED_SOLO_5x5'
        
        # combines rank with tier data and rounds win rate to proper value with 2 decimal places
        rank = rank + ' ' + tier
        winRate = winRate * 100
        winRate = round(winRate, 2)

        await displayembedRanked(ctx, search, rank, winRate, topChamp, level, rankType)
    else:
        await displayembedUnranked(ctx, search, level)
        
# prints in descending order ranked data of discord members with name in database
@client.command()
async def leaderboard(ctx):
    query = '''SELECT league_name FROM username_data'''
    cursor.execute(query)
    names = cursor.fetchall()
    await displayLeaderboard(ctx, names)

@client.command()
async def displayLeaderboard(ctx, names):
    embed = discord.Embed(
        title = 'Leaderboard',
        color = discord.Colour.blurple()
    )

    for i in names:
        summoner = watcher.summoner.by_name(my_region, i['league_name'])  
        summoner_data = watcher.league.by_summoner(my_region, summoner['id'])      # type: ignore

        level = summoner['summonerLevel']  # type: ignore
        choice = 1
        
        try:
            summoner_data[0]  # type: ignore
        except IndexError:
            choice = 0
            
        if choice == 1:
            champion_data = watcher.champion_mastery.by_summoner(my_region, summoner['id'])  # type: ignore
            topChampID = champion_data[0]['championId']  # type: ignore
            latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']  # type: ignore
            static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
            champ_dict = {}

            for key in static_champ_list['data']:  # type: ignore
                row = static_champ_list['data'][key]  # type: ignore
                champ_dict[row['key']] = row['id']
            print(summoner_data[0]['queueType'])  # type: ignore
            if summoner_data[0]['queueType'] != 'RANKED_SOLO_5x5':   # type: ignore
                rank = summoner_data[1]['tier']    # type: ignore
                tier = summoner_data[1]['rank']    # type: ignore
                winRate = round(summoner_data[1]['wins'] / (summoner_data[1]['losses'] + summoner_data[1]['wins']), 2)  # type: ignore
            else:
                rank = summoner_data[0]['tier']  # type: ignore
                tier = summoner_data[0]['rank']    #type: ignore
                winRate = round(summoner_data[0]['wins'] / (summoner_data[0]['losses'] + summoner_data[0]['wins']), 2)  # type: ignore
        
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

# displays ranked information
@client.command()
async def displayembedRanked(ctx, author, rank, winRate, topChamp, level, rankType):
    
    # gets the profile picture for top champion
    s = "Square.png"
    champName = topChamp + s
    champ = discord.File("/home/ubuntu/Version 2.0/Champion Pictures/"
    + champName, filename = champName)
        
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
    embed.add_field(name = 'Top Champion', value = topChamp, inline = True)

    await ctx.send(file = champ, embed = embed)

# displays unranked information
@client.command()
async def displayembedUnranked(ctx, author, level):
    if author == 'gatoralanw':
        logoName = 'ucflol.png'
    else:
        logoName = 'funnymonkey.jpeg'
    logo = discord.File("images/" + logoName, filename = logoName)

    embed = discord.Embed(  
        title = 'Level',
        description = level,
        color = discord.Colour.blurple()
    )
    
    embed.set_thumbnail(url = "attachment://" + logoName)
    embed.set_author(name = author)
    embed.add_field(name = 'Info', value = 'No Ranked Data Available Dog', inline = True)

    await ctx.send(file = logo, embed = embed)

client.run(DISCORD_TOKEN)