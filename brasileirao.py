#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
import sys

def getDataFromAPI(competition):
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    if not API_KEY:
        raise('API_KEY not loaded. Verify .env')

    url = f'https://api.football-data.org/v4/competitions/{competition.upper()}/standings'
    chave = {'X-Auth-Token': API_KEY}

    try:
        res = requests.get(url, headers=chave)
    except Exception as e:
        raise Exception(f'Fatal Error on requests.get():\n{e}')

    if res.status_code != 200:
        raise Exception(f'API returned an error: {res.status_code}')
    
    data = res.json()
    if data:
        return data
    
    raise Exception('No data return')

def updateFile(folder, file, competition):
    os.makedirs(folder, exist_ok=True)
    
    with open(file, 'w', encoding='utf-8') as f:
        data = getDataFromAPI(competition)
        today_date = str(datetime.now().isoformat())
        
        if data:
            f.write(json.dumps({'last_update': today_date}) + '\n')
            f.write(json.dumps(data, ensure_ascii=False))
        else:
            raise Exception('No data recived')
        
    return data

def getData(competition):
    directory = os.path.expanduser('~')
    folder = os.path.join(directory, 'Sistema', 'Brasileirao API', 'jsons')
    file = os.path.join(folder, f'{competition.lower()}.jsonl')

    if not os.path.exists(file) or '-r' in sys.argv:
        print('Accessing football-data.org API - Updating data')
        data = updateFile(folder, file, competition)
        return data

    try:
        with open(file, 'r', encoding='utf-8') as f:
            file_date = f.readline().strip()
            file_date = json.loads(file_date)
            file_date = datetime.fromisoformat(file_date['last_update'])
            data = f.read().strip()
            data = json.loads(data)
        
        if datetime.now() - file_date > timedelta(minutes=90):
            print('Accessing football-data.org API - Updating data')
            data = updateFile(folder, file, competition)

            print(f'Last update:\n{file_date.strftime("%A, %d/%m/%Y %H:%M (dd/mm/yyyy)")}')

    except Exception:
        print('Accessing football-data.org API - Updating data')
        data = updateFile(folder, file, competition)

    return data

def printTable(data):
    if data is None:
        raise Exception('No data avaliable')

    print(f'======================================================================================\n'
          f'|  # | '
          f'pt '
          f'Team          | '
          f' G | '
          f' W (wRate%) | '
          f' D (dRate%) | '
          f' L (lRate%) | '
          f' GF  GA Dif |\n'
          f'|====|==================|====|=============|=============|=============|=============|')

    for p in data['standings'][0]['table']:
        position = p['position']
        points = p['points']
        name = p["team"]["shortName"]
        playedGames =  p['playedGames']
        won = p['won']
        draw = p['draw']
        lost = p['lost']
        goalsFor = p['goalsFor']
        goalsAgainst = p['goalsAgainst']
        goalDifference = p['goalDifference']

        print(f'| {position:2} | '
              f'{points:2} '
              f'{name:13} | '
              f'{playedGames:2} | '
              f'{won :2} ({won  / playedGames * 100:5.1f}%) | '
              f'{draw:2} ({draw / playedGames * 100:5.1f}%) | '
              f'{lost:2} ({lost / playedGames * 100:5.1f}%) | '
              f'{goalsFor:3} {goalsAgainst:3} {goalDifference:3} |')
    print(f'======================================================================================')

if __name__ == '__main__':
    data = getData('bsa')
    printTable(data)