import discord
import logging
import psycopg2
from dotenv import load_dotenv
from discord.ext import commands
from src.api import RiotAPI
from src.config import discord_token, riot_token, postgres_db, postgres_password, postgres_user, postgres_port, postgres_host
from src.commands import register
from src.commands import rank


class LeagueBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.riot_api = RiotAPI()
        self.my_region = 'na1'
        self.sql_connection = psycopg2.connect(
            database=postgres_db,  
            user=postgres_user,
            password=postgres_password,
            host=postgres_host,
            port=postgres_port
        )
        self.cursor = self.sql_connection.cursor()
        
        # Create a table if it does not exist 
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS summoner_data (
            discord_name VARCHAR(100) PRIMARY KEY,
            riot_id VARCHAR(100),
            summoner_id VARCHAR(100),
            puuid VARCHAR(100)
        );
        '''
        self.cursor.execute(create_table_query)
        self.sql_connection.commit()
        
        self.champ_dict = self.get_champ_list()
    
    def get_champ_list(self):
        champ_list = self.riot_api.get_champion_list_data_dragon()
        champ_dict = {}
        for key in champ_list['data']:
            row = champ_list['data'][key]
            champ_dict[row['key']] = row['id']
        return champ_dict
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')


def main():
    # discord bot token(for connecting to bot)
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set logging level to INFO
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('discord.log', encoding='utf-8', mode='w'),
                  logging.StreamHandler()]  # Also output to console
    )
    intents = discord.Intents.default()
    client = LeagueBot(intents=intents, command_prefix='-')

    # Add the register command from the external file
    client.add_command(register)
    client.add_command(rank)
    
    client.run(discord_token)


if __name__ == '__main__':
    main()