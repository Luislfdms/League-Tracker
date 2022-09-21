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

# connect to mysql database
sql_connection = pymysql.connect(
    host='league-tracker-database.cwn2oakyjrry.us-east-1.rds.amazonaws.com',
    user='admin',
    password='Saberlfdms1',
    database='league_tracker',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = sql_connection.cursor()

cursor.execute("USE league_tracker")

sql_connection.commit()

# accessing riot games API
watcher = LolWatcher('RGAPI-7e41c027-bde3-4775-84e5-9ba1e7441104')
my_region = 'na1'

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def setup(ctx, arg):
    author = ctx.message.author.name

    cursor.execute('''
        INSERT INTO username_data (discord_name, league_name) VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE league_name=%s
        ''', (author, arg, arg))
    sql_connection.commit()
    await ctx.send('Setup succesful!')

@client.command()
async def stats(ctx, search):

    query = '''SELECT league_name FROM username_data
               WHERE discord_name=%s '''
    cursor.execute(query, search)
    leagueName = cursor.fetchone()
    leagueName = leagueName.get('league_name')
   
    summoner = watcher.summoner.by_name(my_region, leagueName)    # type: ignore
    summoner_data = watcher.league.by_summoner(my_region, summoner['id'])      # type: ignore
    champion_data = watcher.champion_mastery.by_summoner(my_region, summoner['id'])  # type: ignore
    topChampID = champion_data[0]['championId']  # type: ignore
    #print(champion_data)
    latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']  # type: ignore
    static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
    champ_dict = {}
    for key in static_champ_list['data']:  # type: ignore
        row = static_champ_list['data'][key]  # type: ignore
        champ_dict[row['key']] = row['id']
    
    #print(champ_dict[str(topChampID)])
    rank = summoner_data[0]['tier']   # type: ignore
    print(summoner_data[0]['queueType'])  # type: ignore
    if summoner_data[0]['queueType'] != 'RANKED_SOLO_5x5':   # type: ignore
        rank = summoner_data[1]['tier']    # type: ignore
        tier = summoner_data[1]['rank']    # type: ignore
    else:
        tier = summoner_data[0]['rank']    #type: ignore
    rank = rank + ' ' + tier
    topChamp = champ_dict[str(topChampID)]
    winRate = round(summoner_data[1]['wins'] / (summoner_data[1]['losses'] + summoner_data[1]['wins']), 2)  # type: ignore
    winRate = winRate * 100
    author = ctx.message.author
    await displayembed(ctx, search, rank, winRate, topChamp)

@client.command()
async def lookup(ctx, search):
    summoner = watcher.summoner.by_name(my_region, search)  
    summoner_data = watcher.league.by_summoner(my_region, summoner['id'])      # type: ignore
    champion_data = watcher.champion_mastery.by_summoner(my_region, summoner['id'])  # type: ignore
    topChampID = champion_data[0]['championId']  # type: ignore

    latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']  # type: ignore
    static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
    champ_dict = {}
    for key in static_champ_list['data']:  # type: ignore
        row = static_champ_list['data'][key]  # type: ignore
        champ_dict[row['key']] = row['id']
  
    rank = summoner_data[0]['tier']    # type: ignore
    tier = summoner_data[0]['rank']  # type: ignore
    rank = rank + ' ' + tier
    topChamp = champ_dict[str(topChampID)]
    winRate = round(summoner_data[1]['wins'] / (summoner_data[1]['losses'] + summoner_data[1]['wins']), 2)  # type: ignore
    winRate = winRate * 100

    author = ctx.message.author
    await displayembed(ctx, author, rank, winRate, topChamp)
    

@client.command()
async def displayembed(ctx, author, rank, winRate, topChamp):
    
    s = "Square.png"
    champName = topChamp + s

    champ = discord.File("/home/ubuntu/Version 2.0/Champion Pictures/" 
    + champName, filename = champName)

    embed = discord.Embed(
        title = 'Rank',
        description = rank,
        color = discord.Colour.blurple()
    )
    
    embed.set_thumbnail(url = "attachment://" + champName)
    embed.set_author(name = author, icon_url = "attachment://" + champName)
    embed.add_field(name = 'Win Rate', value = str(winRate) + '%', inline = True)
    embed.add_field(name = 'Top Champion', value = topChamp, inline = True)
    #embed.add_field(name = 'Position', value = prefPosition, inline = True)

    await ctx.send(file = champ, embed = embed)

client.run(DISCORD_TOKEN)