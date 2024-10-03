import requests
import logging
from src.config import riot_token

class RiotAPI:
    def __init__(self):
        self.riot_token = riot_token
        self.base_url = 'https://na1.api.riotgames.com'
        self.headers = {
            'X-Riot-Token': self.riot_token
        }
    
    def get_summoner_by_name(self, summoner_name: str):
        url = f'{self.base_url}/lol/summoner/v4/summoners/by-name/{summoner_name}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
    
    
    def get_summoner_by_puuid(self, puuid: str):
        url = f'{self.base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
            

    def get_puuid_by_riotid_name(self, riot_id: str):
        url = f'{self.base_url}/riot/account/v1/accounts/by-riot-id/{riot_id}'
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
    
    
    def get_matchlist_by_puuid(self, puuid: str):
        url = f'{self.base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids'
        response = requests.get(url, headers=self.headers)
                
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
            
    
    def get_account_by_riotid(self, riot_id: str):
        riot_id = riot_id.split('#')
        
        url = f'{self.base_url}/riot/account/v1/accounts/by-riot-id/{riot_id[0]}/{riot_id[1]}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
    
    
    def get_match_by_id(self, match_id: str):
        url = f'{self.base_url}/match/v5/matches/{match_id}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
    
    
    def get_champion_mastery_by_summoner_id(self, summoner_id: str):
        url = f'{self.base_url}/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
    
    
    def get_champion_mastery_by_summoner_id_and_champion_id(self, summoner_id: str, champion_id: str):
        url = f'{self.base_url}/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/by-champion/{champion_id}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
    
    
    def get_champion_mastery_score_by_summoner_id(self, summoner_id: str):
        url = f'{self.base_url}/champion-mastery/v4/scores/by-summoner/{summoner_id}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error: {response.status_code}')
    
