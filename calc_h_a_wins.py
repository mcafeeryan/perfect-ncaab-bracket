import math
import csv
import os
from pprint import pprint


def set_default():
	default = {}
	default['ID'] = ''
	default['Games'] = 0
	default['Wins'] = 0
	default['Home Wins'] = 0
	default['Away Wins'] = 0
	default['Neutral Wins'] = 0
	default['Losses'] = 0
	default['Home Losses'] = 0
	default['Away Losses'] = 0
	default['Neutral Losses'] = 0
	return default

indir = 'csv'
outdir = 'training_set'

header = ['ID', 'Games', 'Wins', 'Home Wins', 'Away Wins', 'Neutral Wins', 'Losses', 'Home Losses', 'Away Losses', 'Neutral Losses', 'home_wscore', 'away_wscore', 'neutral_wscore']

#loop through regular_season_results.csv
infile = open(os.path.join(indir, 'regular_season_results.csv'))
dr = csv.DictReader(infile)
outdict = {}
default = set_default()
winrecord = {}

for row in dr:
	wteamid = row['season'] + row['wteam']
	lteamid = row['season'] + row['lteam']
	d = outdict.get(wteamid, default.copy())
	l = outdict.get(lteamid, default.copy())
	d['ID'] = wteamid
	l['ID'] = lteamid
	d['Games'] += 1.0
	l['Games'] += 1.0
	d['Wins'] += 1.0
	l['Losses'] += 1.0
	wloc = row['wloc']

	if wloc == 'N':
		lloc = wloc
		d['Neutral Wins'] += 1.0
		l['Neutral Losses'] += 1.0

	elif wloc == 'H':
		lloc = 'A'
		d['Home Wins'] += 1.0
		l['Away Losses'] += 1.0
	elif wloc == 'A':
		lloc = 'H'
		d['Away Wins'] += 1.0
		l['Home Losses'] += 1.0
	winrecord.setdefault(wteamid, set()).add((wloc,lteamid))
	outdict[wteamid] = d
	outdict[lteamid] = l


for team,scores in outdict.items():
	scores['Home Losses'] = 1.0 if scores['Home Losses'] == 0 else scores['Home Losses']
	outdict[team]['home_wscore'] = scores['Home Wins']/scores['Home Losses']
	scores['Away Losses'] = 1.0 if scores['Away Losses'] == 0 else scores['Away Losses']
	outdict[team]['away_wscore'] = scores['Away Wins']/scores['Away Losses']
	scores['Neutral Losses'] = 1.0 if scores['Neutral Losses'] == 0 else scores['Neutral Losses']
	outdict[team]['neutral_wscore'] = scores['Neutral Wins']/scores['Neutral Losses']

for i in range(10):
	olddict = outdict.copy()
	for team,opps in winrecord.items():
		home_wscore = 0
		away_wscore = 0
		neutral_wscore = 0
		for loc, opp in opps:
			if loc == 'H':
				home_wscore += olddict[opp]['away_wscore']
			elif loc == 'A':
				away_wscore += olddict[opp]['home_wscore']
			elif loc == 'N':
				neutral_wscore += olddict[opp]['neutral_wscore']
		outdict[team]['home_wscore'] = home_wscore
		outdict[team]['away_wscore'] = away_wscore
		outdict[team]['neutral_wscore'] = neutral_wscore
	maxhscore = max([x['home_wscore'] for x in outdict.values()])
	maxascore = max([x['away_wscore'] for x in outdict.values()])
	maxnscore = max([x['neutral_wscore'] for x in outdict.values()])
	for key,team in outdict.items():
		outdict[key]['home_wscore'] = team['home_wscore']/maxhscore
		outdict[key]['away_wscore'] = team['away_wscore']/maxascore
		outdict[key]['neutral_wscore'] = team['neutral_wscore']/maxnscore


outfile = open(os.path.join(outdir, 'win_data.csv'), 'wb')
dw = csv.DictWriter(outfile, fieldnames = header)
dw.writeheader()
dw.writerows(outdict.values())
