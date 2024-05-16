import json
import dataclasses
from datetime import datetime

import requests

HEADERS = {
    'Referer': 'https://www.mlb.com/',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"Linux"',
}

QUERY = 'sportId=1&sportId=51&sportId=21'\
        '&startDate={}&endDate={}'\
        '&timeZone=America/New_York&gameType=E'\
        '&&gameType=S&&gameType=R&&gameType=F'\
        '&&gameType=D&&gameType=L&&gameType=W'\
        '&&gameType=A&&gameType=C&language=en'\
        '&leagueId=104&&leagueId=103&&leagueId=160'\
        '&&leagueId=590&hydrate=team,linescore(matchup),'\
        'venue(location)&sortBy=gameDate,gameStatus,gameType'

API_URL = 'https://statsapi.mlb.com/api/v1/schedule?{q}'

@dataclasses.dataclass
class InningScore:
    runs: int
    hits: int
    errors: int

@dataclasses.dataclass
class Inning:
    num: int
    ordinal: int
    home: InningScore
    away: InningScore

@dataclasses.dataclass
class TotalScore:
    home: InningScore
    away: InningScore

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
    innings: list[Inning] = dataclasses.field(default_factory=list)

def get_inning_score(score: dict) -> InningScore:
    return InningScore(runs=score.get("runs", 0),
                       hits=score.get("hits", 0),
                       errors=score.get("errors", 0))

def get_innings(mlb_innings: list[dict]) -> list[Inning]:
    innings = []

    for mlb_inning in mlb_innings:
        inning = Inning(num=mlb_inning.get("num"),
                        ordinal=mlb_inning.get("ordinalNum"),
                        home=get_inning_score(mlb_inning.get("home", {})),
                        away=get_inning_score(mlb_inning.get("away", {})))
        
        innings.append(inning)
    
    return innings

def request_data() -> dict:
    date_now = datetime.now().date()
    q = QUERY.format(date_now, date_now)
    api_url = API_URL.format(q=q)

    while True:
        try:
            response = requests.get(api_url, headers=HEADERS)

            return response.json()["dates"][-1]
        
        except: pass

def get_game(game: dict) -> Game:
    teams, linescore = game["teams"], game["linescore"]
    home, away = teams["home"], teams["away"]

    home_team = Team(name=home["team"]["name"],
                        mascot=home["team"]["clubName"],
                        short_name=home["team"]["shortName"],
                        abbr_name=home["team"]["abbreviation"],
                        score=home["score"])
    
    away_team = Team(name=away["team"]["name"],
                        mascot=away["team"]["clubName"],
                        short_name=away["team"]["shortName"],
                        abbr_name=away["team"]["abbreviation"],
                        score=away["score"])
    
    total = linescore["teams"]
    scores = TotalScore(home=get_inning_score(total["home"]),
                        away=get_inning_score(total["away"]))
    
    return Game(home=home_team, 
                away=away_team, 
                scores=scores,
                innings=get_innings(linescore["innings"]))

def get_games() -> list[Game]:
    raw_games = request_data()
    processed = []

    with open("./data/sample.json", "w") as f:
        json.dump(raw_games, f, indent=4)

    for game in raw_games.get("games", []):
        try:
            if game["status"]["codedGameState"] == "I":
                processed.append(get_game(game))
        
        except: pass
    
    return processed

with open("./data/games.json", "w") as f:
    games = get_games()

    json.dump([dataclasses.asdict(g) for g in games], f, indent=4)
