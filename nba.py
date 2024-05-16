import json
import dataclasses

import requests

HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'dnt': '1',
    # 'if-modified-since': 'Fri, 10 May 2024 10:27:32 GMT',
    # 'if-none-match': '"7732457fdad5c9877d1f3179b76f6e93"',
    'origin': 'https://www.nba.com',
    'priority': 'u=1, i',
    'referer': 'https://www.nba.com/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

API_URL = 'https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json'

@dataclasses.dataclass
class Period:
    num: int
    ordinal: str
    home: int
    away: int

@dataclasses.dataclass
class TotalScore:
    home: int
    away: int

@dataclasses.dataclass
class Team:
    name: str
    mascot: str
    short_name: str
    abbr_name: str
    score: int

@dataclasses.dataclass
class Game:
    home: Team
    away: Team
    scores: TotalScore
    periods: list[Period] = dataclasses.field(default_factory=list)

def get_periods(home_periods: list[dict], away_periods: list[dict]) -> list[Period]:
    periods = []

    for h_period, a_period in zip(home_periods, away_periods):
        period = Period(num=h_period.get("period"),
                        ordinal=f"Q{h_period.get('period')}",
                        home=h_period.get("score"),
                        away=a_period.get("score"))
        
        periods.append(period)
    
    return periods

def request_data() -> dict:
    while True:
        try:
            response = requests.get(API_URL, headers=HEADERS)

            return response.json()
        
        except: pass

def get_game(game: dict) -> Game:
    home, away = game["homeTeam"], game["awayTeam"]

    home_team = Team(name=f'{home["teamCity"]} {home["teamName"]}',
                     mascot=home["teamName"],
                     short_name=home["teamCity"],
                     abbr_name=home["teamTricode"],
                     score=home["score"])
    
    away_team = Team(name=f'{away["teamCity"]} {away["teamName"]}',
                     mascot=away["teamName"],
                     short_name=away["teamCity"],
                     abbr_name=away["teamTricode"],
                     score=away["score"])
    
    scores = TotalScore(home=home["score"], away=away["score"])
    
    return Game(home=home_team, 
                away=away_team, 
                scores=scores,
                periods=get_periods(home["periods"], away["periods"]))

def get_games() -> list[Game]:
    raw_games = request_data()
    processed = []

    with open("./data/nba_sample.json", "w") as f:
        json.dump(raw_games, f, indent=4)

    for game in raw_games.get("scoreboard", {}).get("games", []):
        processed.append(get_game(game))
    
    return processed

# response = requests.get(, headers=headers)

with open("./data/nba.json", "w") as f:
    processed = get_games()
    json.dump([dataclasses.asdict(g) for g in processed], f, indent=4)