import requests
import json
from gamedata import do_game
TEAM_ID = 152

LEA_TEAM_API_URL = "https://api.leamateur.pro/team/{}"
LEA_GAME_API_URL = "https://api.leamateur.pro/calendar/{}"
class Team: 
    def __init__(self, team_id, team_name) -> None:
        self.team_id = team_id
        self.team_name = team_name
class Player:
    def __init__(self, team, id, nick, position) -> None:
        self.team = team
        self.id = id
        self.nick = nick
        self.position = position
class GamePlayer:
    def __init__(self, player, champ_id, list_items, kills, deaths, assists, cs, runes) -> None:
        self.player = player
        self.champ_id = champ_id
        self.items = list_items
        self.kills = kills
        self.death = deaths
        self.assist = assists
        self.cs =cs
        self.runes =runes

class GameTeam:
    def __init__(self, name, kills, towers, inh,drake,barons,heralds,top,jung,mid,adc,supp):
        self.team_name = name
        self.total_kills =  kills
        self.total_towers = towers
        self.total_inhi = inh
        self.total_drakes = drake
        self.total_barons =  barons
        self.total_heralds =  heralds
        self.top =top
        self.jungler= jung 
        self.mid =  mid
        self.adc =  adc 
        self.support = supp

class Game:
    def __init__(self, team_blue, team_red, time, winner, game_version) -> None:
        self.blue_team = team_blue
        self.red_team = team_red
        self.match_duration = time
        self.winner_team = winner
        self.game_version= game_version


def save_user(team_id, user_id, lol_nick, user_position):
    users_file = open("users.csv", "a")
    users_file.write("{},{},{},{}\n".format(team_id, user_id, lol_nick, user_position))
    users_file.close()
def get_team(team_id, users, teams):
    team_data = requests.get(LEA_TEAM_API_URL.format(team_id)).json()
    teams[team_data["data"]["id"]] = Team(team_data["data"]["id"], team_data["data"]["name"])

    for player in team_data["players"]:
        user_id = player["userId"]
        user_lolnick = player["user"]["summonerName"]
        user_position = player["user"]["position"]
        users[user_id] = Player(teams[team_data["data"]["id"]], user_id, user_lolnick, user_position)
def save_game(game):
    file = open("game_{}.json".format(game["id"]), "w")
    file.write(json.dumps(game))
def main():
    users =  {}
    teams = {}
    get_team(TEAM_ID, users, teams)
    game_number = 0
    print(users)
    team_data = requests.get(LEA_TEAM_API_URL.format(TEAM_ID)).json()
    for game in team_data["gamesPlayed"]:
        match_data = requests.get(LEA_GAME_API_URL.format(game["id"])).json()
        for match in match_data["lolGame"]:
            do_game(game_number, match)
            game_number += 1

main()