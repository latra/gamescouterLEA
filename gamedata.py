import pandas as pd, json, os
from tabulate import tabulate
import xlsxwriter
workbook = xlsxwriter.Workbook('demo.xlsx')
worksheet = workbook.add_worksheet()

def write_excel(rownumber, player_data, match, objectives_data, fist_tower, tower_assisted = ""):


    df = pd.DataFrame(player_data)
    df2 = pd.DataFrame(objectives_data)


    header_format = workbook.add_format({
        "bold": True,
        "fg_color": '#147580',
        "border": 1
    })
    cell_format = workbook.add_format({
        "border": 1
    })
    for col in range (0, 17):
        worksheet.write(rownumber, col,"", header_format)
    worksheet.merge_range(rownumber, 0, rownumber, 15,  match["enemy"], header_format)
    worksheet.merge_range(rownumber, 16,  rownumber, 19, "%s in %.0f minutes" % (match["result"], match["time"]), header_format)
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(rownumber + 1, col_num, value, header_format)          

    for row in range(0, len(df)):
        for col in range(len(df.columns)):
            worksheet.write(row + rownumber + 2, col, df.iat[row,col], cell_format)

    for col_num, value in enumerate(df2.columns.values):
        worksheet.write(rownumber + 1, col_num + 21, value, header_format)

    for row in range(0, len(df2)):
        for col in range(len(df2.columns)):
            worksheet.write(rownumber+ row + 2, col + 21, df2.iat[row,col], cell_format)
    worksheet.write(rownumber + 6, 21, "Posible primera torre:", header_format)
    worksheet.write(rownumber + 6, 22, fist_tower, cell_format)
    worksheet.write(rownumber + 6, 21, "Asistida por:", header_format)
    worksheet.write(rownumber + 6, 22, tower_assisted, cell_format)
    
def get_firsttower(tower_asssits):
    if "TOP" in tower_asssits and  "BOTTOM" not in tower_asssits  and  "MIDDLE" not in tower_asssits :
        return "TOP"
    elif (("BOTTOM" in tower_asssits or "UTILITY" in tower_asssits) and "TOP" not in tower_asssits and "MIDDLE" not in tower_asssits) or ( "TOP" in tower_asssits and  "BOTTOM" in tower_asssits and  "UTILITY" in tower_asssits and  "MIDDLE" not in tower_asssits):
        return "BOT"
    else:
        return "MID"

     
def do_game(game_number, game_data):
    TEAM = 152

    data = []
    # game_data = json.loads(open("games/" + gamefile).read())
    if not game_data["info"]:
        print("game not played")
        return 1
    objective_team_side = 100 if (game_data["teamLolGame"][0]["side"] == "Blue" and game_data["teamLolGame"][0]["team"]["id"] == TEAM) or (game_data["teamLolGame"][1]["side"] == "Blue" and game_data["teamLolGame"][1]["team"]["id"] == TEAM) else 200

    objective_team = game_data["teamLolStats"][0] if  game_data["teamLolStats"][0]["teamId"] == TEAM else game_data["teamLolStats"][1]

    players = {"TOP": [], "JUNGLE": [], "MIDDLE": [], "BOTTOM": [], "UTILITY": []}
    for obj in game_data["playerLolStats"]:
        players[obj["individualPosition"]].append(obj)
    duracion_partida = (game_data["info"]["gameDuration"]) / 60
    first_tower_involved = []
    for line in players:
        
        objective_player = players[line][0] if players[line][0]["teamId"] == objective_team_side else players[line][1]
        enemy_player = players[line][1] if players[line][0]["teamId"] == objective_team_side else players[line][0]

        data.append( {
            "ROL": line,
            "Player": objective_player["summonerName"],
            "Champ": objective_player["championName"],
            "Machup": enemy_player["championName"],
            "K": objective_player["kills"],
            "D": objective_player["deaths"],
            "A": objective_player["assists"],
            "KDA": (objective_player["kills"] + objective_player["assists"]) / objective_player["deaths"] if objective_player["deaths"] != 0 else "PERFECT",
            "KP": ((objective_player["kills"]+objective_player["assists"]) * 100) / objective_team["totalKills"],
            "G": objective_player["goldEarned"],
            "GPM": objective_player["goldEarned"] / duracion_partida,
            "CS":  objective_player["totalMinionsKilled"],
            "CSM":  objective_player["totalMinionsKilled"] /duracion_partida,
            "DMG": objective_player["totalDamageDealtToChampions"],
            "DMGM": objective_player["totalDamageDealtToChampions"] / duracion_partida ,
            "D%": (objective_player["totalDamageDealtToChampions"]*100)/objective_team["totalDmg"], #REVISAR
            "CS@10":  objective_player["challenges"]["laneMinionsFirst10Minutes"],
            "CSD@10":  objective_player["challenges"]["laneMinionsFirst10Minutes"] - enemy_player["challenges"]["laneMinionsFirst10Minutes"],
            "VS": objective_player["visionScore"],
            "TOWER PLATES": objective_player["challenges"]["turretPlatesTaken"],
        })
        if objective_player["firstTowerKill"] == True or objective_player["firstTowerAssist"] == True or  enemy_player["firstTowerKill"] == True or enemy_player["firstTowerAssist"] == True:
            first_tower_involved.append(line)
        


    objectives = [ 
        {
        "Objective": "Tower",
        "First":  str(objective_team["firstTower"]),
        "FirstTime": (objective_team["timeFirstTower"]/1000)/60,
        "Total": objective_team["totalTowers"],
        "EnemyTotal": objective_team["totalTowersEne"],
        },
            {
        "Objective": "Drake",
        "First":  str(objective_team["firstDrake"]),
        "FirstTime": (objective_team["timeFirstDrake"]/1000)/60,
        "Total": objective_team["totalDrakes"],
        "EnemyTotal": objective_team["totalDrakesEne"],
        },
            {
        "Objective": "Herald",
        "First":  str(objective_team["firstHerald"]),
        "FirstTime": (objective_team["timeFirstHerald"]/1000)/60,
        "Total": objective_team["totalHerald"],
        "EnemyTotal": objective_team["totalHeraldEne"],
        },
            {
        "Objective": "Baron",
        "First":  str(objective_team["firstbaron"]),
        "FirstTime": (objective_team["timeFirstBaron"]/1000)/60,
        "Total": objective_team["totalBarons"],
        "EnemyTotal": objective_team["totalBaronsEne"],
        },
    ]
    print(objectives)
    match_data = {
        "time": duracion_partida,
        "result": objective_team["result"].upper(),
        "enemy": game_data["teamLolGame"][1]["team"]["name"] if  game_data["teamLolGame"][0]["teamId"] == TEAM else game_data["teamLolGame"][0]["team"]["name"]
    }
    write_excel((game_number*12) + 1, data,match_data, objectives, get_firsttower(tower_asssits=first_tower_involved), str(first_tower_involved))

# print(first_tower_involved)
# number = 0
# for file in os.listdir("games"):
#     result = do_game(number, file)
#     if not result:
#         number += 1
# workbook.close()
    