import requests
from prettytable import PrettyTable


# import numpy as np
# import matplotlib.pyplot as plt

def pythag_percent(scored, against):
    return scored ** 1.81 / (scored ** 1.81 + against ** 1.81)


def calc_magic_number(teams):
    mnObj = {}
    firstPlaceWins = teams[0]['won']
    secondPlaceLosses = teams[1]['lost']
    mnObj['gamesBack'] = ((teams[0]['won'] - teams[1]['won']) + (teams[1]['lost'] - teams[0]['lost'])) / 2.0
    totalGames = 162
    mnObj['magicNumber'] = totalGames + 1 - firstPlaceWins - secondPlaceLosses
    mnObj['leadingTeam'] = teams[0]['name']
    mnObj['trailingTeam'] = teams[1]['name']
    return mnObj


def map_standings_into_useful_data(standings):
    standings['name'] = "{0} {1}".format(standings['first_name'], standings['last_name'])
    standings['won'] = float(standings['won'])
    standings['lost'] = float(standings['lost'])
    standings['runs_scored'] = float(standings['points_for'])
    standings['runs_against'] = float(standings['points_against'])
    standings['win_percentage'] = standings['won'] / (standings['lost'] + standings['won'])
    standings['pythag_win_percentage'] = pythag_percent(standings['runs_scored'], standings['runs_against'])
    standings['outperformance'] = standings['win_percentage'] - standings['pythag_win_percentage']
    return standings


r = requests.get('https://erikberg.com/mlb/standings.json')
if int(r.status_code) == 200:
    standingsObj = r.json()
    standingsDate = standingsObj['standings_date']
    teamData = list(map(map_standings_into_useful_data, standingsObj['standing']))

    al_east = sorted(filter(lambda x: x['conference'] == "AL" and x['division'] == "E", teamData),
                     key=lambda x: (x['won'], 162 - x['lost']))[::-1]
    al_central = sorted(filter(lambda x: x['conference'] == "AL" and x['division'] == "C", teamData),
                        key=lambda x: (x['won'], 162 - x['lost']))[::-1]
    al_west = sorted(filter(lambda x: x['conference'] == "AL" and x['division'] == "W", teamData),
                     key=lambda x: (x['won'], 162 - x['lost']))[::-1]
    nl_east = sorted(filter(lambda x: x['conference'] == "NL" and x['division'] == "E", teamData),
                     key=lambda x: (x['won'], 162 - x['lost']))[::-1]
    nl_central = sorted(filter(lambda x: x['conference'] == "NL" and x['division'] == "C", teamData),
                        key=lambda x: (x['won'], 162 - x['lost']))[::-1]
    nl_west = sorted(filter(lambda x: x['conference'] == "NL" and x['division'] == "W", teamData),
                     key=lambda x: (x['won'], 162 - x['lost']))[::-1]

    print("As of {0}:".format(standingsDate))
    topTeams = [al_east[:2], al_central[:2], al_west[:2], nl_east[:2], nl_central[:2], nl_west[:2]]
    magicNumbers = sorted(map(calc_magic_number, topTeams), key=lambda x: x['magicNumber'])
    x = PrettyTable(["Leading Team", "Magic Number", "Trailing Team", "Games Back"])
    x.padding_width = 1  # One space between column edges and contents (default)
    for i in magicNumbers:
        magic_num = int(i['magicNumber'])
        if magic_num <= 0:
            magic_num = "CLINCHED"
        x.add_row([i['leadingTeam'], magic_num, i['trailingTeam'], i['gamesBack']])
    print(x)

    outperfData = sorted(teamData, key=lambda x: x['outperformance'])[::-1]
    y = PrettyTable(["Team", "W", "L", "Win %", "pythag %", 'outperformance'])
    y.padding_width = 1
    for tm in outperfData:
        y.add_row([tm['name'], int(tm['won']), int(tm['lost']), "{0} %".format(round(tm['win_percentage'] * 100.0, 2)),
                   "{0} %".format(round(tm['pythag_win_percentage'] * 100.0, 2)),
                   "{0} %".format(round(tm['outperformance'] * 100, 4))])
    print(y)

    # ind = np.arange(len(teamData))
    # width = 0.35
    # outperformance = map(lambda x: x['outperformance'], teamData)
    # teams = map(lambda x: x['name'], teamData)
    # fig, ax = plt.subplots()
    # rects1 = ax.bar(ind, outperformance, width, color='r')
    # ax.set_xticklabels(teams, rotation='vertical')
    # plt.show()
