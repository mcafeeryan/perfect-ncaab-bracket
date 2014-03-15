import math
import csv
import os
from pprint import pprint

indir = 'csv'
outdir = 'training_set'

# Generate a dict of season names
infile = open(os.path.join(indir, 'seasons.csv'))
dr = csv.DictReader(infile)
season_dict = dict([(x['years'], x['season']) for x in dr])
rev_season_dict = dict([(y,x) for x,y in season_dict.items()])
pprint(rev_season_dict)
infile.close()

# Generate a dict of team ids
infile = open(os.path.join(indir, 'teams.csv'))
dr = csv.DictReader(infile, delimiter = '\t')
team_dict = {}
for row in dr:
    team_dict[row['name']] = row['id']
    

# Read in team data
all_teams = {}

header = ['Team Name', 'Total Games', 'Wins', 'Losses', 'Winning Pct', 'Possessions', 'Possessions Per 40 minutes', 'Floor Pct', 'Efficiency', 'Field Goals Made', 'Field Goal Attempts', 'Field Goal Pct', 'Free Throws Made', 'Free Throw Attempts', 'Free Throw Pct', '3-pt Field Goals Made', '3-pt Field Goal Attempts', '3-pt Field Goal Pct', 'Effective Field Goal Pct', 'True Shooting Pct', 'Free Throw Rate', 'Field Goal Point Pct', 'Free Throw Point Pct', '3-pt Field Goal Point Pct', 'Points Per Possessions', 'Points', 'Points Per Game', 'Rebound Pct', 'Total Rebounds', 'Total Rebounds Per Game', 'Offensive Reb Pct', 'Offensive Rebounds', 'Offensive Rebounds Per Game', 'Defensive Reb Pct', 'Defensive Rebounds', 'Defensive Rebounds Per Game', 'Team Rebounds', 'Team Rebounds Per Game', 'Assist Pct', 'Assists', 'Assists Per Game', 'Assist to Turnover', 'Steal Pct', 'Steals', 'Steals Per Game', 'Turnover Pct', 'Turnovers', 'Turnovers Per Game', 'Block Pct', 'Blocks', 'Blocks Per Game', 'Fouls', 'Fouls Per Game', 'Disqualifications']

for yrs, season in season_dict.items():
    try:
        statfile = open(os.path.join(indir, yrs + '_teamstats.csv'))
        oppfile = open(os.path.join(indir, yrs +  '_opponentstats.csv'))
    except IOError:
        print 'No data for season: %s' %yrs
    else:
        statdr = csv.DictReader(statfile, fieldnames = header)
        oppdr = csv.DictReader(oppfile, fieldnames = [x + ' Opp' for x in header])

        for team, opp in zip(statdr, oppdr):
            try:
                teamid = season + team_dict[team['Team Name']]
            except KeyError:
                print 'Kaggle dataset does not have team: %s' %team['Team Name']
            else:
                outdict = team.copy()
                outdict.update(opp)
                outdict['ID'] = teamid
                del(outdict['Team Name Opp'])

                all_teams[teamid] = outdict

header.extend([x + ' Opp' for x in header])
header.remove('Team Name Opp')
header.append('ID')

outfile = open(os.path.join(outdir, 'team_stats.csv'), 'wb')
dw = csv.DictWriter(outfile, fieldnames = header)
dw.writeheader()
dw.writerows(all_teams.values())

# Generate training set of games
infile = open(os.path.join(indir, 'tourney_results.csv'))
outfile = open(os.path.join(outdir, 'training_data.csv'), 'wb')
dr = csv.DictReader(infile)
outarr = []

header.insert(0, 'scorediff')
header.insert(1, 'scoreratio')
header.insert(2, 'year')
header.extend(['daynum','numot'])
dw = csv.DictWriter(outfile, fieldnames = header)

for game in dr:    
    wid = game['season'] + game['wteam']
    lid = game['season'] + game['lteam']

    try:
        wstats = all_teams[wid]
        lstats = all_teams[lid]
    except KeyError:
        pass
    else:
        outdict = {'daynum' : int(game['daynum']),
                   'year' : int(rev_season_dict[game['season']][:4]),
                   'scorediff' : int(game['wscore']) - int(game['lscore']),
                   'scoreratio' : math.log( float(game['wscore']) / float(game['lscore']))}

        for key,wstat in wstats.items():
            lstat = lstats[key]
            try:
                wstat = float(wstat)
                lstat = float(lstat)
            except ValueError:
                pass
            else:
                if lstat == 0:
                    lstat = 1
                if wstat == 0:
                    wstat = 1

                outdict[key] = math.log(wstat/lstat)

        outarr.append(outdict)
        losedict = dict([(key,(-val)) for key,val in outdict.items()])
        losedict['daynum'] = game['daynum']
        losedict['year'] = int(rev_season_dict[game['season']][:4]),
        outarr.append(losedict)

dw.writeheader()
dw.writerows(outarr)
            
            
           
    
