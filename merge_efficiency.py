import math
import csv
import os
from pprint import pprint
from numpy import median
from itertools import tee, izip
import sys

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def make_seasons_array():
    base = '20'
    years = []
    seasons = []
    for num in range(3,15): 
        if len(str(num)) < 2:
            start = base + '0' + str(num)
        else:
            start = base + str(num)
        years.append(start)
    for start, end in pairwise(years):
        season = start + '-' + end
        seasons.append(season)
    return (years, seasons)

def set_default():
	default = {}
	default['ID'] = ''
	default['Median Height'] = []
	default['Median Weight'] = []
	default['Max Height'] = 0
	default['Max Weight'] = 0
	default['Senior Count'] = 0
	default['Junior Count'] = 0
	default['Sophomore Count'] = 0
	default['Freshman Count'] = 0
	return default

indir = 'csv'
outdir = 'training_set'

header = ['ID', 'Median Height', 'Median Weight', 'Max Height', 'Max Weight', 'Senior Count', 'Junior Count', 'Sophomore Count', 'Freshman Count']

#get a dictionary of seasons to kaggle season id
infile = open(os.path.join(indir, 'seasons.csv'))
dr = csv.DictReader(infile)
season_dict = dict([(x['years'], x['season']) for x in dr])

# Generate a dict of team ids
infile = open(os.path.join(indir, 'teams.csv'))
dr = csv.DictReader(infile, delimiter = '\t')
team_dict = dict([(x['ss_name'], x['id']) for x in dr])

#loop through each [seaon]_players.csv file
(years,seasons) = make_seasons_array()
default = set_default()
outdict = {}
for season in seasons:
	infile = open(season + "_players.csv",'r')
	dr = csv.DictReader(infile, delimiter = ',')
		
	for row in dr:
		if row['Height'] == '':
			continue
		
		team = row['Team']
		if team == 'Team':
			continue
		try:
			teamid = season_dict[season] + team_dict[team]
		except KeyError:
			print "kaggle data set didn't have team " + team 
			continue

		d = outdict.get(teamid, set_default())
		d['ID'] = teamid
		try:
			d['Median Height'].append(int(row['Height']))
			d['Median Weight'].append(float(row['Weight']))
		except:
			print row['Height']
			print row
			print season
			sys.exit()
		
		year = row['Age']
		if year == 'Freshman':
			d['Freshman Count'] += 1

		elif year == 'Sophomore':
			d['Sophomore Count'] += 1

		elif year == 'Junior':
			d['Junior Count'] += 1

		elif year == 'Senior':
			d['Senior Count'] += 1
		outdict[teamid] = d
	
for team, d in outdict.items():
	outdict[team]['Max Height'] = max(outdict[team]['Median Height'])
	outdict[team]['Max Weight'] = max(outdict[team]['Median Weight'])
	outdict[team]['Median Height'] = median(outdict[team]['Median Height'])
	outdict[team]['Median Weight'] = median(outdict[team]['Median Weight'])

name = 'pchars.csv'
outfile = open(os.path.join(outdir, name), 'a')
dw = csv.DictWriter(outfile, fieldnames = header)
dw.writeheader()
dw.writerows(outdict.values())
infile.close()
outfile.close()
