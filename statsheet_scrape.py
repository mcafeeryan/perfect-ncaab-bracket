from bs4 import BeautifulSoup
from selenium import webdriver
import string, re
from itertools import tee, izip

def get_page(url):

	print "getting url: " + url
	driver = webdriver.PhantomJS()
	driver.get(url)
	data = driver.page_source

	driver.quit()
	soup = BeautifulSoup(data)

	return soup

def get_teams():
	
	alphabet = list(string.ascii_uppercase)
	baseUrl = "http://statsheet.com/mcb/teams/browse/name?t="

	for letter in alphabet:
		url = baseUrl + letter
		soup = get_page(url)

		for table in soup.findAll("tbody"):
			for tr in table.findAll("tr"):
				tds = tr.findAll("td")
				if len(tds):
					outputFile = open('textfiles/teams_statsheet.txt', 'a')
					line = str(tds[1].text) + "," + str(tds[1].a['href']) + "," + str(tds[2].text)
					outputFile.write(line + "\n")
					outputFile.close()

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def make_seasons_array():
	base = '20'
	arr = []
	ret = []
	for num in range(3,15):	
		if len(str(num)) < 2:
			start = base + '0' + str(num)
		else:
			start = base + str(num)
		arr.append(start)
	for start, end in pairwise(arr):
		season = start + '-' + end
		ret.append(season)
	return ret

def get_stats():

	teamFile = open('textfiles/teams_statsheet.txt', 'r')
	
	# TargetURL
	# http://statsheet.com/mcb/teams/syracuse/team_stats?season=2013-2014&type=all
	
	seasons = make_seasons_array()
	extraPart = '/team_stats?season=' + season + '&type=all'

	# url = 'http://statsheet.com/mcb/teams/syracuse/team_stats?type=all'
	url = "http://statsheet.com/mcb/teams/nebraska-omaha/team_stats?type=all"
	thearray = [url]
	for url in thearray:

		# splitLine = team.strip("\n").split(",")
		# teamName = splitLine[0]
		# teamURL = splitLine[1]

		teamName = "Nebraska-Omaha"
		# url = teamURL + extraPart

		soup = get_page(url)
		# print soup
		for table in soup.findAll("table", { "class" : "table-stats" }):

			valueStr = ""
			for tr in table.findAll("tr"):
				tds = tr.findAll("td")

				# this are the values
				if len(tds):
					valueStr += str(tds[1].text) + ","

			if valueStr != "":
				valueStr = valueStr[:-1]
				statFile = open('test.txt', 'a')
				statFile.write(teamName + "," + valueStr + "\n")
				statFile.close()

	teamFile.close()

def get_games():
	team_file = open('textfiles/teams.txt', 'r')
	lines = team_file.readlines()

	for line in lines:
		line_array = line.split(",")
		if len(line_array) < 2:
			continue
		team_name = line_array[0]
		url = line_array[1]
		soup = get_page(url)
		gameFile = open('textfiles/games.txt', 'a')
		for tr in soup.findAll("tr"):
			ret_line = ""
			if tr["class"][0] not in ['stathead', 'colhead']:
				game_status = tr.findAll("li", {"class":"game-status"})
				opponent_team_name= tr.findAll("li", {"class":"team-name"})[0].text

				opponent_team_name = opponent_team_name.replace("*","") 
				opponent_team_name = re.sub(r'^#\d{1,2}[\W_]? ',"", opponent_team_name)
				# opponent_team_name = re.sub(r'\([^\(]*\)',"", opponent_team_name)
				if len(game_status)>1:

					if game_status[0].text == "@":
						ret_line+=opponent_team_name+","
						ret_line+=team_name+","
						if game_status[1].span.text == "W":
							ret_line+= "L"
						else:
							ret_line+= "W"
					else:
						ret_line+=team_name+","
						ret_line+=opponent_team_name+","

						if game_status[1].span.text == "W":
							ret_line+= "W"
						else:
							ret_line+= "L"
			ret_line+="\n"
			if ret_line != "\n":
				gameFile.write(ret_line)
	gameFile.close()
				

def main():
	# get_teams()
	get_stats()
	# get_games()

main()