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

header = ['ID', 'Games', 'Wins', 'Home Wins', 'Away Wins', 'Neutral Wins', 'Losses', 'Home Losses', 'Away Losses', 'Neutral Losses']

#loop through regular_season_results.csv
infile = open(os.path.join(indir, 'regular_season_results.csv'))
dr = csv.DictReader(infile)
outdict = {}
default = set_default()

for row in dr:
	wteamid = row['season'] + row['wteam']
	lteamid = row['season'] + row['lteam']
	d = outdict.get(wteamid, default.copy())
	l = outdict.get(lteamid, default.copy())
	d['ID'] = wteamid
	l['ID'] = lteamid
	d['Games'] += 1
	l['Games'] += 1
	d['Wins'] += 1
	l['Losses'] += 1
	wloc = row['wloc']
	if wloc == 'N':
		lloc = wloc
		d['Neutral Wins'] += 1
		l['Neutral Losses'] += 1
	elif wloc == 'H':
		lloc = 'A'
		d['Home Wins'] += 1
		l['Away Losses'] += 1
	elif wloc == 'A':
		lloc = 'H'
		d['Away Wins'] += 1
		l['Home Losses'] += 1
	outdict[wteamid] = d
	outdict[lteamid] = l

outfile = open(os.path.join(outdir, 'win_data.csv'), 'wb')
dw = csv.DictWriter(outfile, fieldnames = header)
dw.writeheader()
dw.writerows(outdict.values())
