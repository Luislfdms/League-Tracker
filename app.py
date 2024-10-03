import discord
import logging
import psycopg2
from dotenv import load_dotenv
from discord.ext import commands
from src.api import RiotAPI
from src.config import discord_token, riot_token, db_password, db_host, db_user, db_name, db_port
from src.commands import register
from src.commands import lookup
from src.commands import stats


class LeagueBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.watcher = LolWatcher(riot_token)
        self.my_region = 'na1'
        self.sql_connection = psycopg2.connect(
            database=db_name,  
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        self.cursor = self.sql_connection.cursor()
        
        # Create a table if it does not exist (example table creation)
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS username_data (
            discord_name VARCHAR(255) PRIMARY KEY,
            league_name VARCHAR(255)
        );
        '''
        self.cursor.execute(create_table_query)
        self.sql_connection.commit()
    
    def get_champ_list(self):
        latest = self.watcher.data_dragon.versions_for_region(self.my_region)['n']['champion']
        static_champ_list = self.watcher.data_dragon.champions(latest, False, 'en_US')
        champ_dict = {}
        for key in static_champ_list['data']:
            row = static_champ_list['data'][key]
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
    client.add_command(lookup)
    client.add_command(stats)
    
    client.run(discord_token)


if __name__ == '__main__':
    main()