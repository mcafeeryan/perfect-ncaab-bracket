import math
import csv
import os
from pprint import pprint
from unidecode import unidecode

indir = 'csv'
outdir = 'training_set'

# Generate a dict of season names
infile = open(os.path.join(indir, 'seasons.csv'))
dr = csv.DictReader(infile)
season_dict = dict([(x['years'], x['season']) for x in dr])
rev_season_dict = dict([(y,x) for x,y in season_dict.items()])
del(season_dict['2013-2014'])
infile.close()

# Generate a dict of team ids
infile = open(os.path.join(indir, 'teams.csv'))
dr = csv.DictReader(infile, delimiter = '\t')
team_dict = {}
tr_team_dict = {}
for row in dr:
    team_dict[row['ss_name']] = row['id']
    tr_team_dict[row['tr_name']] = unidecode(row['id'])

# Read in team clusters
infile = open(os.path.join(indir, 'team_clusters.csv'))
dr = csv.DictReader(infile)
clust_dict = {}
for row in dr:
    clust_dict[row['teamstats.ID']] = row['clust.cluster']
    
    
# Read in home/away losses
infile = open(os.path.join('training_set', 'win_data.csv'))
dr = csv.DictReader(infile)
win_dict = {}
for row in dr:
    myid = row['ID']
    del(row['ID'])
    win_dict[myid] = row

# Read in win eigenvector scores
infile = open(os.path.join(indir, 'eigenscores.csv'))
dr = csv.DictReader(infile)
eigen_dict = {}
for row in dr:
    eigen_dict[row['ID']] = row
    
# Read in TeamRankings data
tr_dict = {}
for yrs, season in season_dict.items():
    yr = yrs[:4]
    try:
        offeff = open(os.path.join(indir, 'EFF/'+yrs+'O.csv'))
        defeff = open(os.path.join(indir, 'EFF/'+yrs+'D.csv'))
        SOS = open(os.path.join(indir, 'SOS/' + yrs + 'SOS.csv'))
        ESC = open(os.path.join(indir, 'ESC/'+yrs +'ESC.csv'))
        
    except IOError:
        'No data for season: %s' %yrs
    else:
        offdr = csv.DictReader(offeff)
        defdr = csv.DictReader(defeff)
        sosdr = csv.DictReader(SOS)
        escdr = csv.DictReader(ESC)

        for row in offdr:
            teamid = season + tr_team_dict[unidecode(row['Team']).strip()]
            tr_dict.setdefault(teamid,{})['OffEff'] = row[yr]
        for row in defdr:
            teamid = season + tr_team_dict[unidecode(row['Team'].strip())]
            tr_dict.setdefault(teamid,{})['DefEff'] = row[yr]
        for row in sosdr:
            tname = unidecode(row['Team']).strip()
            try:
                teamid = season + tr_team_dict[tname]    
            except KeyError:
                print 'Bad Team: %s' %tname
            else:            
                tr_dict.setdefault(teamid, {})['SOS'] = row['Rating']
        for row in escdr:
            teamid = season + tr_team_dict[unidecode(row['Team']).strip()]
            tr_dict.setdefault(teamid, {})['ESC'] = row[yr]

# Read in StatSheet data and merge
all_teams = {}

header = ['Team Name', 'Total Games', 'Wins', 'Losses', 'Winning Pct', 'Possessions', 'Possessions Per 40 minutes', 'Floor Pct', 'Efficiency', 'Field Goals Made', 'Field Goal Attempts', 'Field Goal Pct', 'Free Throws Made', 'Free Throw Attempts', 'Free Throw Pct', '3-pt Field Goals Made', '3-pt Field Goal Attempts', '3-pt Field Goal Pct', 'Effective Field Goal Pct', 'True Shooting Pct', 'Free Throw Rate', 'Field Goal Point Pct', 'Free Throw Point Pct', '3-pt Field Goal Point Pct', 'Points Per Possessions', 'Points', 'Points Per Game', 'Rebound Pct', 'Total Rebounds', 'Total Rebounds Per Game', 'Offensive Reb Pct', 'Offensive Rebounds', 'Offensive Rebounds Per Game', 'Defensive Reb Pct', 'Defensive Rebounds', 'Defensive Rebounds Per Game', 'Team Rebounds', 'Team Rebounds Per Game', 'Assist Pct', 'Assists', 'Assists Per Game', 'Assist to Turnover', 'Steal Pct', 'Steals', 'Steals Per Game', 'Turnover Pct', 'Turnovers', 'Turnovers Per Game', 'Block Pct', 'Blocks', 'Blocks Per Game', 'Fouls', 'Fouls Per Game', 'Disqualifications']

for yrs, season in season_dict.items():
    yr = yrs[:4]
    try:
        statfile = open(os.path.join(indir, yrs + '_teamstats.csv'))
        oppfile = open(os.path.join(indir, yrs +  '_opponentstats.csv'))
    except IOError:
        print 'No data for season: %s' %yrs
    else:
        # Statsheet data
        statdr = csv.DictReader(statfile, fieldnames = header)
        oppdr = csv.DictReader(oppfile, fieldnames = [x + ' Opp' for x in header])
    
        for team, opp in zip(statdr, oppdr):
            try:
                teamid = season + team_dict[team['Team Name']]
            except KeyError:
                print 'No Kaggle data for team: %s' %team['Team Name']
            else:
                outdict = team.copy()
                try:
                    windata = win_dict[teamid]
                except KeyError:
                    print 'No Wins data for team: %s' %team['Team Name']
                else:
                    outdict.update(opp)

                try:
                    trdata = tr_dict[teamid]
                except KeyError:
                    print 'No TeamRankings data for team: %s' %team['Team Name']
                else:
                    outdict.update(trdata)
                    
                try:
                    evdata = eigen_dict[teamid]
                except KeyError:
                    print 'No Eigenvector scores for team: %s' %team['Team Name']
                else:
                    outdict.update(evdata)
                    
                #del(outdict['Team Name Opp'])

                outdict.update(windata)

                try:
                    outdict['Pace Forcing'] =  abs(float(outdict['Possessions Per 40 minutes']) - float(outdict['Possessions Per 40 minutes Opp']))
                except KeyError:
                    print 'No Pace Forcing scores for team: %s' %team['Team Name']


                all_teams[teamid] = outdict

header.extend(win_dict.values()[0].keys())
header.extend([x + ' Opp' for x in header])
header.append('ID')
header.extend(['OffEff','DefEff', 'SOS', 'ESC', 'locwtevcent', 'uwevcent','scwtevcent', 'revevcent', 'Pace Forcing'])

outfile = open(os.path.join(outdir, 'team_stats.csv'), 'wb')
tsdw = csv.DictWriter(outfile, fieldnames = header)
tsdw.writeheader()
written_teams = set()

# Read in info on previous matchups
infile = open('training_set/winlose_network.csv')
dr = csv.DictReader(infile,fieldnames = ['lteam','wteam','scoreratio','loc'])
prev_matches = {}
for row in dr:
    wgamekey = (row['wteam'], row['lteam'])
    lgamekey = (row['lteam'], row['wteam'])
    prev_matches[wgamekey] = prev_matches.get(wgamekey,0) + float(row['scoreratio'])
    prev_matches[lgamekey] = prev_matches.get(lgamekey,0) - float(row['scoreratio'])

# Generate training set of games
infile = open(os.path.join(indir, 'tourney_results.csv'))
outfile = open(os.path.join(outdir, 'training_data.csv'), 'wb')
dr = csv.DictReader(infile)
outarr = []


header.insert(0, 'scorediff')
header.insert(1, 'scoreratio')
header.insert(2, 'year')
header.extend(['daynum','numot','class_matchup'])

for game in dr:    
    wid = game['season'] + game['wteam']
    lid = game['season'] + game['lteam']
    gamekey = (wid,lid)
    try:
        wstats = all_teams[wid]
        lstats = all_teams[lid]
    except KeyError:
        pass
    else:
        outdict = {'daynum' : int(game['daynum']),
                   'year' : int(rev_season_dict[game['season']][:4]),
                   'scorediff' : int(game['wscore']) - int(game['lscore']),
                   'scoreratio' : math.log( float(game['wscore']) / float(game['lscore'])),
                   'class_matchup' : int(clust_dict[wid] + clust_dict[lid])}

        if gamekey in prev_matches:
            outdict['prev_matches'] = prev_matches[gamekey]
        else:
            outdict['prev_matches'] = 0
        
        if wid not in written_teams:
            tsdw.writerow(all_teams[wid])
            written_teams.add(wid)
        if lid not in written_teams:
            tsdw.writerow(all_teams[lid])
            written_teams.add(lid)

        for key,wstat in wstats.items():
            lstat = lstats[key]
            try:
                wstat = float(wstat)
                lstat = float(lstat)
            except TypeError:
                print 'TypeError %s: wstat - float(%s); lstat - float(%s) ' %(key, wstat, lstat)
                wstat = 0.0
                lstat = 0.0
            except ValueError:
                wstat = 0.0
                lstat = 0.0
            
            if lstat == 0:
                lstat = 1
            if wstat == 0:
                wstat = 1
            try:
                if key == 'ESC':
                    outdict[key] = wstat-lstat
                else:
                    outdict[key] = math.log(wstat/lstat)
            except:
                print 'Log Error %s: wstat - float(%s); lstat - float(%s) ' %(key, wstat, lstat)

        def get_logratio(statA, statB, Loser = False):
            if Loser:
                Astats = lstats
                Bstats = wstats
            else:
                Astats = wstats
                Bstats = lstats

            return math.log(float(Astats[statA])/float(Bstats[statB]))
                        
        losedict = dict([(key,(-val)) for key,val in outdict.items()])
        losedict['daynum'] = game['daynum']
        losedict['year'] = int(rev_season_dict[game['season']][:4]),
        losedict['class_matchup'] = clust_dict[lid] + clust_dict[wid]

        for statdict,wl in [(outdict,False),(losedict,True)]:
            statdict['foulrate 2 FTR'] = get_logratio('Fouls Per Game','Free Throw Rate',wl)
            statdict['foulrate 2 FTPct'] =  get_logratio('Fouls Per Game', 'Free Throw Pct',wl)
            statdict['DefReb 2 OffReb'] = get_logratio('Defensive Reb Pct', 'Offensive Reb Pct',wl)
            statdict['3 pt Weakness Pct'] = get_logratio('3-pt Field Goal Point Pct Opp', '3-pt Field Goal Pct',wl)
            statdict['3 pt Weakness Point Pct']  = get_logratio('3-pt Field Goal Point Pct Opp', '3-pt Field Goal Point Pct',wl)
            statdict['TO 2 Steal'] = get_logratio('Turnover Pct', 'Steal Pct',wl)
        
        outarr.append(outdict)
        outarr.append(losedict)
        
header.extend(['prev_matches','foulrate 2 FTR', 'foulrate 2 FTPct', '3 pt Weakness Pct', '3 pt Weakness Point Pct', 'DefReb 2 OffReb', 'TO 2 Steal'])
dw = csv.DictWriter(outfile, fieldnames = header)
dw.writeheader()
dw.writerows(outarr)
            
            
           
    
